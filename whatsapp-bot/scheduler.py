#!/usr/bin/env python3
"""
定时提醒功能
使用 schedule 实现定时发送WhatsApp提醒 + 智能规则
"""

# 先加载环境变量
from dotenv import load_dotenv
import os
if os.path.exists(".env"):
    load_dotenv(override=True)

import schedule
import time
import requests
import json
import random
from datetime import datetime, timedelta, timezone
import re
import pytz
from meta_whatsapp_service import MetaWhatsAppService
from routes.webhook import log_to_file
from config import Config

# 心率分段调试开关：将环境变量 DEBUG_HR_SEGMENTS 设为 "1" 可开启详细分段日志
DEBUG_HR_SEGMENTS = (os.environ.get('DEBUG_HR_SEGMENTS') or '0') == '1'

try:
    from supabase import create_client
except Exception:
    create_client = None

class WhatsAppScheduler:
    def __init__(self):
        self.meta_service = MetaWhatsAppService()
        self.api_base_url = self._get_api_base_url()
        self.default_template_lang = os.environ.get('FALLBACK_TEMPLATE_LANG', 'en_US')
        # 新加坡时区
        self.sgt = pytz.timezone('Asia/Singapore')
        # Supabase
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.supabase_key = os.environ.get('SUPABASE_API_KEY')
        self.sb = None
        if create_client and self.supabase_url and self.supabase_key:
            try:
                self.sb = create_client(self.supabase_url, self.supabase_key)
                log_to_file("✅ Supabase 客户端初始化成功")
            except Exception as e:
                log_to_file(f"❌ Supabase 客户端初始化失败: {e}")
        # 入组贴士内容（前9条含来源，第10条无来源）
        self.onboarding_tips = [
            "Tip #1: 150 minutes is what you need\nAdapted from: https://diabetes.org/health-wellness/fitness/weekly-exercise-targets",
            "Tip #2: Spread it out\nAdapted from: https://diabetes.org/health-wellness/fitness/weekly-exercise-targets",
            "Tip #3: Shorten your sessions\nAdapted from: https://diabetes.org/health-wellness/fitness/weekly-exercise-targets",
            "Tip #4: Setting smart goals\nAdapted from: https://diabetes.org/health-wellness/fitness/weekly-exercise-targets",
            "Tip #5: Fine-tuning your fitness level\nAdapted from: https://diabetes.org/health-wellness/fitness/weekly-exercise-targets",
            "Tip #6: Make time for fitness\nAdapted from: https://diabetes.org/health-wellness/fitness/weekly-exercise-targets",
            "Tip #6: How to stay motivated\nAdapted from: https://diabetes.org/health-wellness/fitness/weekly-exercise-targets",
            "Tip #7: Have fun.\nAdapted from: https://diabetes.org/health-wellness/fitness/weekly-exercise-targets",
            "Tip #8: Track your progress.\nAdapted from: https://diabetes.org/health-wellness/fitness/weekly-exercise-targets",
            "Tip #9: Excuse-proof your plan.\nAdapted from: https://diabetes.org/health-wellness/fitness/weekly-exercise-targets",
            "Tip #10: Check your blood sugar before and after exercise."
        ]

    # ---------- 语言与模板选择 ----------
    def _get_patient_language(self, patient) -> str:
        """返回模板/文本语言代码：'en_US' 或 'zh_CN'"""
        # 优先从 Supabase 患者记录读取
        pid = str(patient.get('id') or patient.get('patient_id') or '')
        preferred = None
        if pid and self.sb:
            try:
                rec = self.get_patient_record(pid) or {}
                preferred = (rec.get('preferred_language') or '').lower()
            except Exception:
                preferred = None
        if not preferred:
            # 兼容来自前端的字段
            preferred = (patient.get('preferred_language') or '').lower()
        if preferred in ('zh', 'zh_cn', 'cn', 'chinese'):
            return 'zh_CN'
        return 'en_US'

    def _localize(self, zh_text: str, en_text: str, lang_code: str) -> str:
        return en_text if lang_code == 'en_US' else zh_text
    
    def _get_api_base_url(self):
        """智能处理 FORWARD_URL，确保 API 调用使用正确的基础 URL"""
        forward_url = os.environ.get('FORWARD_URL', 'http://localhost:3005')
        
        # 如果 FORWARD_URL 包含 /chat/message，则移除这个路径作为 API 基础 URL
        if '/chat/message' in forward_url:
            # 移除 /chat/message 部分，保留基础 URL
            base_url = forward_url.replace('/chat/message', '')
            log_to_file(f"🔧 检测到 FORWARD_URL 包含 /chat/message，API 基础 URL 设为: {base_url}")
            return base_url
        else:
            # 直接使用 FORWARD_URL 作为 API 基础 URL
            log_to_file(f"🔧 使用 FORWARD_URL 作为 API 基础 URL: {forward_url}")
            return forward_url
        
    def get_patients_from_api(self):
        """从后端API获取患者列表"""
        log_to_file("📞 开始获取患者列表...")
        
        try:
            # 从 Supabase 获取所有患者
            if not self.sb:
                log_to_file("❌ 无 Supabase 客户端")
                return []
            
            # 获取所有患者
            res = (self.sb
                   .table('patients')
                   .select('id, full_name, phone_number')
                   .not_.is_('phone_number', 'null')
                   .neq('phone_number', '')
                   .execute())
            
            if res.data:
                patients = res.data
                log_to_file(f"✅ 成功获取 {len(patients)} 个患者")
                return patients
            else:
                log_to_file("⚠️ 未找到任何患者")
                return []
                
        except Exception as e:
            log_to_file(f"❌ 获取患者列表异常: {e}")
            return []

    def get_patients_from_supabase(self):
        """直接从 Supabase 获取患者列表（回退方案）"""
        if not self.sb:
            log_to_file("⚠️ 无 Supabase 客户端，无法回退获取患者")
            return []
        try:
            # 仅选择必要字段，过滤有手机号的患者
            res = (self.sb
                   .table('patients')
                   .select('id, full_name, phone_number')
                   .not_.is_('phone_number', 'null')
                   .limit(500)
                   .execute())
            rows = res.data or []
            # 适配 send_exercise_reminder 需要的字段命名
            patients = []
            for r in rows:
                patients.append({
                    'id': r.get('id'),
                    'full_name': r.get('full_name') or '用户',
                    'phone_number': r.get('phone_number') or ''
                })
            log_to_file(f"✅ 从 Supabase 获取患者: {len(patients)} 条")
            return patients
        except Exception as e:
            log_to_file(f"❌ Supabase 获取患者失败: {e}")
            return []

    # ---------- Supabase 数据访问与规则计算 ----------
    def get_patient_record(self, patient_id: str):
        if not self.sb:
            return None
        try:
            # 尝试将字符串转换为整数，如果失败则返回None
            try:
                patient_id_int = int(patient_id)
            except (ValueError, TypeError):
                log_to_file(f"❌ 无效的患者ID格式: {patient_id}")
                return None
            
            res = self.sb.table('patients').select('*').eq('id', patient_id_int).single().execute()
            return res.data
        except Exception as e:
            log_to_file(f"❌ 获取患者记录失败 {patient_id}: {e}")
            return None

    def get_workouts_between(self, patient_id: str, start_iso: str, end_iso: str):
        """获取workouts数据 - 注意：当前workouts表存储的是会话数据，不是运动记录"""
        if not self.sb:
            return []
        try:
            # 尝试将字符串转换为整数，如果失败则返回空列表
            try:
                patient_id_int = int(patient_id)
            except (ValueError, TypeError):
                log_to_file(f"❌ 无效的患者ID格式: {patient_id}")
                return []
            
            # 查询workouts表，但注意这个表存储的是会话数据，不是运动记录
            res = (self.sb
                   .table('workouts')
                   .select('*')
                   .eq('patient_id', patient_id)  # 使用patient_id，并且保持字符串格式
                   .gte('start_date', start_iso)
                   .lte('start_date', end_iso)
                   .execute())
            
            # 处理真实的运动数据
            workout_records = []
            for workout in (res.data or []):
                # 直接使用workouts表中的真实数据
                workout_record = {
                    'id': workout.get('id', ''),
                    'patient_id': workout.get('patient_id', patient_id),
                    'start_date': workout.get('start_date', ''),
                    'duration': workout.get('duration', 0),
                    'steps': workout.get('steps', 0),
                    'distance': workout.get('distance', 0.0),
                    'calories': workout.get('calories', 0),
                    'moderate_intensity': workout.get('moderate_intensity', 0),
                    'vigorous_intensity': workout.get('vigorous_intensity', 0),
                    'heartrate_data': workout.get('heartrate_data', []),
                    'exercise_type': 'General Exercise',  # 默认运动类型
                    'created_at': workout.get('created_at', '')
                }
                workout_records.append(workout_record)
            
            return workout_records
        except Exception as e:
            log_to_file(f"❌ 获取workouts失败 {patient_id}: {e}")
            return []

    def get_weight_between(self, patient_id: str, start_iso: str, end_iso: str):
        """获取体重数据 - 目前数据库中无独立体重表，返回空列表"""
        # TODO: 如果将来有体重数据表，在这里实现查询逻辑
        return []

    def get_blood_pressure_between(self, patient_id: str, start_iso: str, end_iso: str):
        """获取血压数据 - 目前数据库中无独立血压表，返回空列表"""
        # TODO: 如果将来有血压数据表，在这里实现查询逻辑
        return []

    def get_heart_rate_between(self, patient_id: str, start_iso: str, end_iso: str):
        """获取心率数据 - 注意：当前workouts表没有心率数据，返回空列表"""
        if not self.sb:
            return []
        try:
            # 当前workouts表存储的是会话数据，没有心率信息
            # 返回空列表，表示没有心率数据
            log_to_file(f"ℹ️ 当前workouts表无心率数据，返回空列表 {patient_id}")
            return []
        except Exception as e:
            log_to_file(f"❌ 获取heart_rate失败 {patient_id}: {e}")
            return []

    @staticmethod
    def compute_minutes_at_or_above(heartrate_data, threshold: int) -> int:
        """计算高于阈值的心率分钟数（按时间戳差值，累计完后四舍五入）"""
        if not heartrate_data or len(heartrate_data) == 0:
            return 0

        # 解析心率数据
        try:
            if isinstance(heartrate_data, str):
                import json
                hr_list = json.loads(heartrate_data)
            else:
                hr_list = heartrate_data
        except Exception as e:
            log_to_file(f"❌ 解析心率数据失败: {e}")
            return 0

        if not isinstance(hr_list, list) or len(hr_list) == 0:
            return 0

        from datetime import datetime

        def parse_iso(ts: str):
            try:
                return datetime.fromisoformat(ts)
            except Exception:
                return datetime.fromisoformat(ts.replace('+08:00', ''))

        # 预处理排序
        timeline = []
        for p in hr_list:
            if not isinstance(p, dict):
                continue
            try:
                dt = parse_iso(str(p.get('date', '')))
            except Exception:
                continue
            hr = int(p.get('heartrate', 0))
            timeline.append((dt, hr))

        if len(timeline) < 2:
            return 0

        timeline.sort(key=lambda x: x[0])

        # 检查数据点时间间隔
        if len(timeline) > 1:
            first_dt = timeline[0][0]
            last_dt = timeline[-1][0]
            total_span_seconds = (last_dt - first_dt).total_seconds()
            total_span_minutes = total_span_seconds / 60
            avg_interval = total_span_seconds / (len(timeline) - 1) if len(timeline) > 1 else 0
            log_to_file(f"🔍 心率数据时间跨度(阈值计算): {first_dt} 到 {last_dt} = {total_span_minutes:.1f}分钟, 平均间隔={avg_interval:.1f}秒, 数据点数={len(timeline)}")

        total_seconds = 0
        above_start_time = None
        segments_above = []  # (start_dt, end_dt, seconds)

        for dt, hr in timeline:
            if hr >= threshold:
                if above_start_time is None:
                    above_start_time = dt
            else:
                if above_start_time is not None:
                    secs = max(0, (dt - above_start_time).total_seconds())
                    total_seconds += secs
                    if DEBUG_HR_SEGMENTS:
                        segments_above.append((above_start_time, dt, int(secs)))
                        log_to_file(f"✅ >= {threshold} bpm结算: {above_start_time} ~ {dt} = {secs}s ({secs/60:.2f}m)")
                    above_start_time = None

        # 收尾
        last_dt = timeline[-1][0]
        if above_start_time is not None:
            secs = max(0, (last_dt - above_start_time).total_seconds())
            total_seconds += secs
            if DEBUG_HR_SEGMENTS:
                segments_above.append((above_start_time, last_dt, int(secs)))
                log_to_file(f"✅ >= {threshold} bpm结算(收尾): {above_start_time} ~ {last_dt} = {secs}s ({secs/60:.2f}m)")

        total_minutes = round(total_seconds / 60)
        if DEBUG_HR_SEGMENTS:
            for s, e, secs in segments_above:
                mins = round(secs / 60)
                log_to_file(f"✅ >= {threshold} bpm segment: {s} ~ {e} = {secs}s ≈ {mins}m")
        log_to_file(f"🔍 心率计算: 阈值={threshold}, 数据点数={len(timeline)}, 达标={total_seconds}秒={total_minutes}分钟")
        return total_minutes
    
    @staticmethod
    def compute_intensity_minutes(heartrate_data, moderate_hr_min: int, moderate_hr_max: int, 
                                 vigorous_hr_min: int, vigorous_hr_max: int, 
                                 max_gap_seconds: int = 300) -> tuple:
        """
        根据患者心率区间计算moderate和vigorous intensity分钟数
        只计算连续的心率数据段（相邻数据点间隔小于max_gap_seconds的视为连续）
        
        Args:
            heartrate_data: 心率数据列表
            moderate_hr_min: 中等强度心率下限
            moderate_hr_max: 中等强度心率上限  
            vigorous_hr_min: 高强度心率下限
            vigorous_hr_max: 高强度心率上限
            max_gap_seconds: 最大连续间隔（秒），默认300秒（5分钟），超过此间隔视为新段
            
        Returns:
            tuple: (moderate_minutes, vigorous_minutes) - 四舍五入到分钟
        """
        if not heartrate_data or len(heartrate_data) == 0:
            return 0, 0
        
        # 解析心率数据
        try:
            if isinstance(heartrate_data, str):
                import json
                hr_list = json.loads(heartrate_data)
            else:
                hr_list = heartrate_data
        except Exception as e:
            log_to_file(f"❌ 解析心率数据失败: {e}")
            return 0, 0
        
        if not isinstance(hr_list, list) or len(hr_list) == 0:
            return 0, 0
        
        from datetime import datetime

        def parse_iso(ts: str):
            try:
                return datetime.fromisoformat(ts)
            except Exception:
                # 回退：去掉显式 +08:00 再解析
                return datetime.fromisoformat(ts.replace('+08:00', ''))

        # 预处理为 (dt, hr) 并按时间排序
        timeline = []
        for p in hr_list:
            if not isinstance(p, dict):
                continue
            try:
                dt = parse_iso(str(p.get('date', '')))
            except Exception:
                continue
            hr = int(p.get('heartrate', 0))
            timeline.append((dt, hr))

        if len(timeline) < 2:
            return 0, 0

        timeline.sort(key=lambda x: x[0])

        # 检查数据点时间间隔
        if len(timeline) > 1:
            first_dt = timeline[0][0]
            last_dt = timeline[-1][0]
            total_span_seconds = (last_dt - first_dt).total_seconds()
            total_span_minutes = total_span_seconds / 60
            avg_interval = total_span_seconds / (len(timeline) - 1) if len(timeline) > 1 else 0
            log_to_file(f"🔍 心率数据时间跨度: {first_dt} 到 {last_dt} = {total_span_minutes:.1f}分钟, 平均间隔={avg_interval:.1f}秒, 数据点数={len(timeline)}")

        # 将时间线分割为连续段（相邻点间隔 <= max_gap_seconds）
        continuous_segments = []
        current_segment = [timeline[0]]
        
        for i in range(1, len(timeline)):
            prev_dt = timeline[i-1][0]
            curr_dt = timeline[i][0]
            gap_seconds = (curr_dt - prev_dt).total_seconds()
            
            if gap_seconds <= max_gap_seconds:
                # 连续，添加到当前段
                current_segment.append(timeline[i])
            else:
                # 不连续，结束当前段，开始新段
                if len(current_segment) >= 2:  # 至少2个点才能形成时长
                    continuous_segments.append(current_segment)
                if DEBUG_HR_SEGMENTS:
                    log_to_file(f"⚠️ 检测到间隔: {prev_dt} 到 {curr_dt} = {gap_seconds/60:.1f}分钟，开始新段")
                current_segment = [timeline[i]]
        
        # 添加最后一段
        if len(current_segment) >= 2:
            continuous_segments.append(current_segment)
        
        log_to_file(f"🔍 识别出 {len(continuous_segments)} 个连续数据段（最大间隔={max_gap_seconds}秒）")

        # 在每个连续段内计算强度时间
        moderate_seconds = 0
        vigorous_seconds = 0
        segments_moderate = []
        segments_vigorous = []

        for seg_idx, segment in enumerate(continuous_segments):
            if DEBUG_HR_SEGMENTS:
                seg_start = segment[0][0]
                seg_end = segment[-1][0]
                seg_duration = (seg_end - seg_start).total_seconds() / 60
                log_to_file(f"📊 处理连续段 #{seg_idx+1}: {seg_start} ~ {seg_end} = {seg_duration:.2f}分钟, {len(segment)}个数据点")
            
            moderate_start_time = None
            vigorous_start_time = None

            for idx in range(len(segment)):
                dt, hr_value = segment[idx]

                in_vigorous = vigorous_hr_min <= hr_value <= vigorous_hr_max
                in_moderate = (not in_vigorous) and (moderate_hr_min <= hr_value <= moderate_hr_max)

                if in_vigorous:
                    # 开启/保持 vigorous，关闭 moderate 段并结算
                    if vigorous_start_time is None:
                        vigorous_start_time = dt
                    if moderate_start_time is not None:
                        secs = max(0, (dt - moderate_start_time).total_seconds())
                        moderate_seconds += secs
                        if DEBUG_HR_SEGMENTS:
                            segments_moderate.append((moderate_start_time, dt, int(secs)))
                            log_to_file(f"🧩 MOD结算(段#{seg_idx+1}): {moderate_start_time} ~ {dt} = {secs}s ({secs/60:.2f}m)")
                        moderate_start_time = None
                elif in_moderate:
                    # 开启/保持 moderate，关闭 vigorous 段并结算
                    if moderate_start_time is None:
                        moderate_start_time = dt
                    if vigorous_start_time is not None:
                        secs = max(0, (dt - vigorous_start_time).total_seconds())
                        vigorous_seconds += secs
                        if DEBUG_HR_SEGMENTS:
                            segments_vigorous.append((vigorous_start_time, dt, int(secs)))
                            log_to_file(f"🔥 VIG结算(段#{seg_idx+1}): {vigorous_start_time} ~ {dt} = {secs}s ({secs/60:.2f}m)")
                        vigorous_start_time = None
                else:
                    # 退出所有区间，结算已有区间
                    if moderate_start_time is not None:
                        secs = max(0, (dt - moderate_start_time).total_seconds())
                        moderate_seconds += secs
                        if DEBUG_HR_SEGMENTS:
                            segments_moderate.append((moderate_start_time, dt, int(secs)))
                            log_to_file(f"🧩 MOD结算(退出,段#{seg_idx+1}): {moderate_start_time} ~ {dt} = {secs}s ({secs/60:.2f}m)")
                        moderate_start_time = None
                    if vigorous_start_time is not None:
                        secs = max(0, (dt - vigorous_start_time).total_seconds())
                        vigorous_seconds += secs
                        if DEBUG_HR_SEGMENTS:
                            segments_vigorous.append((vigorous_start_time, dt, int(secs)))
                            log_to_file(f"🔥 VIG结算(退出,段#{seg_idx+1}): {vigorous_start_time} ~ {dt} = {secs}s ({secs/60:.2f}m)")
                        vigorous_start_time = None

            # 段内收尾：若最后仍在某区间，则结算到段内最后一个时间点
            last_dt_in_segment = segment[-1][0]
            if moderate_start_time is not None:
                secs = max(0, (last_dt_in_segment - moderate_start_time).total_seconds())
                moderate_seconds += secs
                if DEBUG_HR_SEGMENTS:
                    segments_moderate.append((moderate_start_time, last_dt_in_segment, int(secs)))
                    log_to_file(f"🧩 MOD结算(收尾,段#{seg_idx+1}): {moderate_start_time} ~ {last_dt_in_segment} = {secs}s ({secs/60:.2f}m)")
            if vigorous_start_time is not None:
                secs = max(0, (last_dt_in_segment - vigorous_start_time).total_seconds())
                vigorous_seconds += secs
                if DEBUG_HR_SEGMENTS:
                    segments_vigorous.append((vigorous_start_time, last_dt_in_segment, int(secs)))
                    log_to_file(f"🔥 VIG结算(收尾,段#{seg_idx+1}): {vigorous_start_time} ~ {last_dt_in_segment} = {secs}s ({secs/60:.2f}m)")
        
        # 转换为分钟并四舍五入
        moderate_minutes = round(moderate_seconds / 60)
        vigorous_minutes = round(vigorous_seconds / 60)
        
        if DEBUG_HR_SEGMENTS:
            for s, e, secs in segments_moderate:
                mins = round(secs / 60)
                log_to_file(f"🧩 MOD segment: {s} ~ {e} = {secs}s ≈ {mins}m")
            for s, e, secs in segments_vigorous:
                mins = round(secs / 60)
                log_to_file(f"🔥 VIG segment: {s} ~ {e} = {secs}s ≈ {mins}m")
        log_to_file(f"🔍 强度计算: 中等强度={moderate_seconds}秒={moderate_minutes}分钟, 高强度={vigorous_seconds}秒={vigorous_minutes}分钟, 连续段数={len(continuous_segments)}, 数据点数={len(hr_list)}")
        return moderate_minutes, vigorous_minutes
    


    def send_exercise_tip(self, patient):
        """发送运动贴士：周一、周三、周五 08:00"""
        name = patient.get('full_name', '用户')
        phone = re.sub(r'\D', '', (patient.get('phone_number') or ''))
        if not phone:
            return False
        if len(phone) == 8:
            phone = '65' + phone
        
        # 随机选择一条贴士
        random_tip = random.choice(self.onboarding_tips)
        tip_message = f"💡 Tip: {random_tip}"
        
        log_to_file(f"📝 发送运动贴士给 {name}: {random_tip[:50]}...")
        result = self.meta_service.send_message(phone, tip_message)
        if isinstance(result, dict) and 'error' in result:
            log_to_file(f"❌ 贴士消息发送失败: {result}")
            return False
        else:
            log_to_file(f"✅ 贴士消息发送成功: {result}")
            return True

    def send_sync_tracker_reminder(self, patient):
        """同步手环提醒：周一、周三、周五 08:00"""
        name = patient.get('full_name', '用户')
        phone = re.sub(r'\D', '', (patient.get('phone_number') or ''))
        if not phone:
            return False
        if len(phone) == 8:
            phone = '65' + phone
        
        msg = ("Please remember to sync your activity tracker today. "
               "Your data helps us better understand exercise patterns better. "
               "It only takes a moment — thank you for your support!")
        
        log_to_file(f"🛰️ 发送同步提醒给 {name}")
        result = self.meta_service.send_message(phone, msg)
        if isinstance(result, dict) and 'error' in result:
            log_to_file(f"❌ 同步提醒发送失败: {result}")
            return False
        else:
            log_to_file(f"✅ 同步提醒发送成功: {result}")
            return True
        
    def send_resistance_reminder(self, patient):
        """阻力训练提醒：每周二/四 08:00（单条模板或文本）"""
        name = patient.get('full_name', '用户')
        lang = self._get_patient_language(patient)
        phone = re.sub(r'\D', '', (patient.get('phone_number') or ''))
        if not phone:
            return False
        if len(phone) == 8:
            phone = '65' + phone
        
        msg = (
            f"Hi {name}! Let's schedule a resistance workout today (bands/dumbbells/bodyweight) 💪\n"
            f"Cover major muscle groups, 8–12 reps per set, 2–3 sets, progress gradually.\n"
            f"Reference video: https://www.youtube.com/watch?v=lhTif8q1zwA&list=PL-CkGc3Da6cRdqKXFfBOUrDh9VB54uljc"
        )
        # 直接发送文本消息
        result = self.meta_service.send_message(phone, msg)
        if isinstance(result, dict) and 'error' in result:
            log_to_file(f"❌ 文本消息发送失败: {result}")
            return False
        else:
            log_to_file(f"✅ 文本消息发送成功: {result}")
            return True

    def send_daily_template(self, patient):
        """每天发送模板消息（用于打开24小时窗口）"""
        phone = re.sub(r'\D', '', (patient.get('phone_number') or ''))
        if len(phone) == 8:
            phone = '65' + phone
        if not phone or len(phone) < 10:
            log_to_file(f"❌ 无效的手机号: {patient.get('phone_number')}")
            return False
        
        # 从环境变量获取模板名称
        template_name = os.environ.get('FALLBACK_TEMPLATE_NAME', 'exercise_opt_in_v1')
        # 模板语言是 "en"（根据查询结果）
        template_lang = "en"
        
        # 获取患者姓名（模板需要 {{1}} 参数）
        patient_name = patient.get('full_name') or patient.get('patient_id') or 'Friend'
        
        # 构建 components 参数（包含姓名）
        components = [
            {
                "type": "BODY",
                "parameters": [
                    {
                        "type": "text",
                        "text": patient_name
                    }
                ]
            }
        ]
        
        log_to_file(f"📤 发送模板消息给 {patient_name} ({phone}): {template_name}/{template_lang}, 参数: {patient_name}")
        result = self.meta_service.send_template_message(phone, template_name, template_lang, components)
        
        # 详细记录响应结果
        log_to_file(f"🔍 模板消息API响应类型: {type(result)}, 内容: {result}")
        
        if isinstance(result, dict):
            if 'error' in result:
                log_to_file(f"❌ 模板消息发送失败: {patient_name} ({phone}), 错误: {result}")
                return False
            elif 'messages' in result:
                # 成功响应包含 messages 字段
                message_id = result.get('messages', [{}])[0].get('id', 'N/A')
                message_status = result.get('messages', [{}])[0].get('message_status', 'N/A')
                log_to_file(f"✅ 模板消息发送成功: {patient_name} ({phone}), 消息ID: {message_id}, 状态: {message_status}")
                return True
            else:
                # 其他情况也视为成功（可能是不同的响应格式）
                log_to_file(f"✅ 模板消息发送成功: {patient_name} ({phone}), 响应: {result}")
                return True
        else:
            log_to_file(f"⚠️ 模板消息响应格式异常: {patient_name} ({phone}), 类型: {type(result)}, 值: {result}")
            return False

    def send_weekly_summary_and_adjust(self, patient):
        """每周总结（单条）：从 patient 表和 workouts 表直接读取数据并计算"""
        if not self.sb:
            return
        pid = str(patient.get('id') or patient.get('patient_id') or '')
        if not pid:
            return
        
        # 从 patient 表获取患者信息
        try:
            patient_res = self.sb.table('patients').select('*').eq('id', pid).execute()
            if not patient_res.data:
                log_to_file(f"❌ 未找到患者记录: {pid}")
                return
            patient_rec = patient_res.data[0]
        except Exception as e:
            log_to_file(f"❌ 获取患者记录失败 {pid}: {e}")
            return
        
        # 获取患者参数
        target_min_hr = int(patient_rec.get('target_min_hr') or 110)
        target_week = int(patient_rec.get('target_duration_week') or 45)
        moderate_hr_min = int(patient_rec.get('moderate_hr_min') or 110)
        moderate_hr_max = int(patient_rec.get('moderate_hr_max') or 140)
        vigorous_hr_min = int(patient_rec.get('vigorous_hr_min') or 140)
        vigorous_hr_max = int(patient_rec.get('vigorous_hr_max') or 180)

        # 计算时间范围（上周：周一到周日）
        now = datetime.now(timezone.utc)
        
        # 计算上周的周一和周日
        # 获取当前是周几（0=周一，6=周日）
        current_weekday = now.weekday()
        # 计算上周一的日期
        last_monday = now - timedelta(days=current_weekday + 7)
        # 计算上周日的日期
        last_sunday = last_monday + timedelta(days=6)
        
        # 设置时间范围（上周一到上周日）
        start_dt = last_monday
        end_dt = last_sunday + timedelta(days=1)  # 包含上周日整天
        start = start_dt.isoformat()
        end = end_dt.isoformat()
        
        log_to_file(f"📅 周总结时间范围: {start_dt.strftime('%Y-%m-%d')} 到 {last_sunday.strftime('%Y-%m-%d')}")
        
        # 从 workouts 表获取运动数据
        try:
            workouts_res = (self.sb.table('workouts')
                          .select('*')
                          .eq('patient_id', pid)
                          .gte('start_date', start)
                          .lt('start_date', end)
                          .execute())
            workouts = workouts_res.data or []
        except Exception as e:
            log_to_file(f"❌ 获取运动数据失败 {pid}: {e}")
            workouts = []

        # 只检查运动数据
        has_any_data = len(workouts) > 0
        log_to_file(f"📊 上周运动数据统计: 运动{len(workouts)}条")
        
        # 若上周无任何记录，回退到最近有数据的一周（最多回退8周）
        if not has_any_data:
            log_to_file(f"🔍 上周无数据，开始回退搜索...")
            for i in range(1, 9):
                # 计算回退的周一到周日
                alt_monday = last_monday - timedelta(weeks=i)
                alt_sunday = alt_monday + timedelta(days=6)
                alt_start = alt_monday.isoformat()
                alt_end = (alt_sunday + timedelta(days=1)).isoformat()
                
                log_to_file(f"🔍 检查第{i}周: {alt_monday.strftime('%Y-%m-%d')} 到 {alt_sunday.strftime('%Y-%m-%d')}")
                
                # 只检查运动数据
                week_has_data = False
                alt_workouts = []
                
                try:
                    # 检查运动数据
                    alt_workouts_res = (self.sb.table('workouts')
                                      .select('*')
                                      .eq('patient_id', pid)
                                      .gte('start_date', alt_start)
                                      .lt('start_date', alt_end)
                                      .execute())
                    alt_workouts = alt_workouts_res.data or []
                    
                    week_has_data = len(alt_workouts) > 0
                        
                except Exception as e:
                    log_to_file(f"❌ 获取第{i}周历史数据失败 {pid}: {e}")
                    continue
                
                if week_has_data:
                    workouts = alt_workouts
                    # 更新日期范围用于显示
                    start_dt = alt_monday
                    end_dt = alt_sunday
                    start = alt_start
                    end = alt_end
                    log_to_file(f"✅ 找到第{i}周有数据: {alt_monday.strftime('%Y-%m-%d')} 到 {alt_sunday.strftime('%Y-%m-%d')}")
                    break
            else:
                log_to_file(f"⚠️ 过去8周都无数据，使用空数据生成总结")
        
        # 计算运动统计
        minutes_moderate = 0
        minutes_vigorous = 0
        total_duration = 0
        total_steps = 0
        total_calories = 0
        
        for w in workouts:
            # 从 workouts 表直接获取数据
            duration = int(w.get('duration', 0))
            steps = int(w.get('steps', 0))
            calories = float(w.get('calories', 0))
            
            total_duration += duration
            total_steps += steps
            total_calories += calories
            
            # 获取心率数据
            hr_list = w.get('heartrate_data') or []
            
            # 计算中等强度和高强度时间（使用正确的区间）
            moderate_min, vigorous_min = WhatsAppScheduler.compute_intensity_minutes(
                hr_list, moderate_hr_min, moderate_hr_max, vigorous_hr_min, vigorous_hr_max
            )
            minutes_moderate += moderate_min
            minutes_vigorous += vigorous_min
            
            # 调试日志
            log_to_file(f"🔍 运动记录 {w.get('id')}: 中等强度={moderate_min}, 高强度={vigorous_min}, 心率数据点数={len(hr_list)}")
        
        # 达标时间 = 中等强度时间 + 高强度时间（所有有效运动时间）
        minutes_at_target = minutes_moderate + minutes_vigorous

        name = patient.get('full_name', '用户')
        phone = re.sub(r'\D', '', (patient.get('phone_number') or ''))
        if phone and len(phone) == 8:
            phone = '65' + phone

        lang = self._get_patient_language(patient)
        
        # 明确日期范围（按 SGT 显示 YYYY-MM-DD）
        # 使用实际的时间范围，而不是假设的7天
        start_sgt = start_dt.astimezone(self.sgt).strftime('%Y-%m-%d')
        end_sgt = end_dt.astimezone(self.sgt).strftime('%Y-%m-%d')
        
        # 计算周目标（从patient表获取）
        weekly_target_moderate = int(patient_rec.get('weekly_target_moderate') or 150)  # 默认150分钟
        
        # 计算剩余需要的运动时间
        remaining_moderate_needed = max(0, weekly_target_moderate - minutes_moderate)
        


        # 生成周一报告：Recap weekly exercise summary
        # 检查是否达标
        if minutes_moderate >= weekly_target_moderate:
            # 达标情况
            summary = (
                f"Recap weekly exercise summary ({start_sgt} to {end_sgt}):\n"
                f"Duration of moderate intensity exercise (minutes): {minutes_moderate}\n"
                f"Duration of vigorous intensity exercise (minutes): {minutes_vigorous}\n"
                f"Target duration of moderate intensity exercise last week (minutes): {weekly_target_moderate}\n"
                f"You met the target duration! Keep it up!"
            )
        else:
            # 未达标情况（包括无运动数据）
            summary = (
                f"Recap weekly exercise summary ({start_sgt} to {end_sgt}):\n"
                f"Duration of moderate intensity exercise (minutes): {minutes_moderate}\n"
                f"Duration of vigorous intensity exercise (minutes): {minutes_vigorous}\n"
                f"Target duration of moderate intensity exercise last week (minutes): {weekly_target_moderate}\n"
                f"You completed {minutes_moderate} minutes of moderate intensity exercise. You required {weekly_target_moderate} minutes to reach your target. You can do it this week!"
            )
        
        # 达标则（仅数据库更新），不再单独再发一条消息
        if minutes_at_target >= target_week:
            new_hr = 120 if target_min_hr < 120 else target_min_hr
            new_week = 60 if target_week < 60 else target_week
            try:
                self.sb.table('patients').update({
                    'target_min_hr': new_hr,
                    'target_duration_week': new_week
                }).eq('id', pid).execute()
                log_to_file(f"🔧 已上调目标: {pid} -> HR {new_hr}, WEEK {new_week}")
            except Exception as e:
                log_to_file(f"❌ 上调目标失败 {pid}: {e}")
        
        # 发送周总结消息（中午12点发送，不包含贴士）
        try:
            result = self.meta_service.send_message(phone, summary)
            if isinstance(result, dict) and 'error' in result:
                log_to_file(f"❌ 周总结消息发送失败: {result}")
            else:
                log_to_file(f"✅ 周总结消息发送成功: {result}")
        except Exception as e:
            log_to_file(f"❌ 发送周总结消息失败 {pid}: {e}")

    def send_midweek_summary(self, patient, period: str):
        """周中汇总：从 patient 表和 workouts 表直接读取数据并计算
        - period == 'mon_tue': 统计周一-周二
        - period == 'mon_thu': 统计周一-周四
        缺失日期按0计，不补发多条，仅发送一条模板或降级文本
        """
        if not self.sb:
            return
        pid = str(patient.get('id') or patient.get('patient_id') or '')
        if not pid:
            return

        # 从 patient 表获取患者信息
        try:
            patient_res = self.sb.table('patients').select('*').eq('id', pid).execute()
            if not patient_res.data:
                log_to_file(f"❌ 未找到患者记录: {pid}")
                return
            patient_rec = patient_res.data[0]
        except Exception as e:
            log_to_file(f"❌ 获取患者记录失败 {pid}: {e}")
            return

        # 获取患者参数
        target_min_hr = int(patient_rec.get('target_min_hr') or 110)
        moderate_hr_min = int(patient_rec.get('moderate_hr_min') or 110)
        moderate_hr_max = int(patient_rec.get('moderate_hr_max') or 140)
        vigorous_hr_min = int(patient_rec.get('vigorous_hr_min') or 140)
        vigorous_hr_max = int(patient_rec.get('vigorous_hr_max') or 180)

        today_sgt = datetime.now(self.sgt)
        # 找到当前周一（以SGT为准），再转UTC时间段
        weekday = today_sgt.weekday()  # 周一=0
        monday_sgt = today_sgt - timedelta(days=weekday)
        monday_sgt = monday_sgt.replace(hour=0, minute=0, second=0, microsecond=0)

        if period == 'mon_tue':
            end_sgt = monday_sgt + timedelta(days=2)  # 周三0点，不含
            label = 'Mon–Tue'
        else:
            end_sgt = monday_sgt + timedelta(days=3)  # 周五0点，不含
            label = 'Mon–Thu'

        # 转UTC ISO 区间
        start_utc = monday_sgt.astimezone(timezone.utc).isoformat()
        end_utc = end_sgt.astimezone(timezone.utc).isoformat()
        
        # 从 workouts 表获取运动数据
        try:
            workouts_res = (self.sb.table('workouts')
                          .select('*')
                          .eq('patient_id', pid)
                          .gte('start_date', start_utc)
                          .lt('start_date', end_utc)
                          .execute())
            workouts = workouts_res.data or []
        except Exception as e:
            log_to_file(f"❌ 获取运动数据失败 {pid}: {e}")
            workouts = []

        # 统计运动数据
        minutes_at_target = 0
        minutes_moderate = 0
        minutes_vigorous = 0
        total_duration = 0
        total_steps = 0
        total_calories = 0
        
        for w in workouts:
            # 从 workouts 表直接获取数据
            duration = int(w.get('duration', 0))
            steps = int(w.get('steps', 0))
            calories = float(w.get('calories', 0))
            
            total_duration += duration
            total_steps += steps
            total_calories += calories
            
            # 使用新的心率区间计算方式
            hr_list = w.get('heartrate_data') or []
            moderate_min, vigorous_min = WhatsAppScheduler.compute_intensity_minutes(
                hr_list, moderate_hr_min, moderate_hr_max, vigorous_hr_min, vigorous_hr_max
            )
            minutes_moderate += moderate_min
            minutes_vigorous += vigorous_min
            
            # 调试日志
            log_to_file(f"🔍 运动记录 {w.get('id')}: 中等强度={moderate_min}, 高强度={vigorous_min}, 心率数据点数={len(hr_list)}")
        
        # 达标时间 = 中等强度时间 + 高强度时间（所有有效运动时间）
        minutes_at_target = minutes_moderate + minutes_vigorous

        name = patient.get('full_name', 'User')
        phone = re.sub(r'\D', '', (patient.get('phone_number') or ''))
        if phone and len(phone) == 8:
            phone = '65' + phone

        # 格式化日期范围
        start_date = monday_sgt.strftime('%Y-%m-%d')
        # end_date 是结束日期的前一天（因为end_sgt是结束日期的0点，不含）
        end_date_actual = (end_sgt - timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = end_sgt.strftime('%Y-%m-%d')
        
        # 记录时间范围用于验证
        log_to_file(f"📅 {label}报告时间范围: {start_date} 到 {end_date_actual} (查询范围: {start_utc} 到 {end_utc})")
        
        # 计算周目标（从patient表获取）
        weekly_target_moderate = int(patient_rec.get('weekly_target_moderate') or 150)  # 默认150分钟
        
        # 计算剩余需要的运动时间
        remaining_moderate_needed = max(0, weekly_target_moderate - minutes_moderate)
        
        if len(workouts) > 0:
            if period == 'mon_thu':
                # 周五总结使用新模板
                summary = (
                    f"End of week exercise summary ({label}, {start_date} to {end_date_actual})\n"
                    f"Duration of moderate intensity exercise (minutes): {minutes_moderate}\n"
                    f"Duration of vigorous intensity exercise (minutes): {minutes_vigorous}\n"
                    f"Target duration of moderate intensity exercise this week (minutes): {weekly_target_moderate}\n"
                    f"Required duration of moderate intensity exercise to achieve weekly target (minutes): {remaining_moderate_needed}\n"
                    f"You can do it!"
                )
            else:
                # 周三总结保持原模板
                summary = (
                    f"Midweek exercise summary ({label}, {start_date} to {end_date_actual})\n"
                    f"Duration of moderate intensity exercise (minutes): {minutes_moderate}\n"
                    f"Duration of vigorous intensity exercise (minutes): {minutes_vigorous}\n"
                    f"Target duration of moderate intensity exercise this week (minutes): {weekly_target_moderate}\n"
                    f"Required duration of moderate intensity exercise to achieve weekly target (minutes): {remaining_moderate_needed}"
                )
        else:
            if period == 'mon_thu':
                # 周五总结无数据时使用新模板
                summary = (
                    f"End of week exercise summary ({label}, {start_date} to {end_date_actual})\n"
                    f"Duration of moderate intensity exercise (minutes): 0\n"
                    f"Duration of vigorous intensity exercise (minutes): 0\n"
                    f"Target duration of moderate intensity exercise this week (minutes): {weekly_target_moderate}\n"
                    f"Required duration of moderate intensity exercise to achieve weekly target (minutes): {remaining_moderate_needed}\n"
                    f"You can do it!"
                )
            else:
                # 周三总结无数据时保持原模板
                summary = (
                    f"Midweek exercise summary ({label}, {start_date} to {end_date_actual})\n"
                    f"Duration of moderate intensity exercise (minutes): 0\n"
                    f"Duration of vigorous intensity exercise (minutes): 0\n"
                    f"Target duration of moderate intensity exercise this week (minutes): {weekly_target_moderate}\n"
                    f"Required duration of moderate intensity exercise to achieve weekly target (minutes): {remaining_moderate_needed}\n"
                )
            log_to_file(f"📭 患者 {name} 本周无运动数据，发送{label}中期汇总模板")

        # 直接发送文本消息
        result = self.meta_service.send_message(phone, summary)
        if isinstance(result, dict) and 'error' in result:
            log_to_file(f"❌ 文本消息发送失败: {result}")
        else:
            log_to_file(f"✅ 文本消息发送成功: {result}")
    
    
    
    def start_scheduler(self):
        """启动定时任务"""
        print("🚀 启动WhatsApp定时提醒服务...")
        log_to_file("🚀 启动WhatsApp定时提醒服务...")
        
        # 设置时区为新加坡时间
        def sgt_time():
            return datetime.now(self.sgt)
        
        print("📅 正在设置定时任务...")
        print(f"🌏 使用新加坡时区: {self.sgt}")
        
        # ========== 新时间表调度 ==========
        # 周一：8am 贴士，12 noon 报告（上周一至周日）
        # 周二/四：8am 阻力提醒
        # 周三：8am 贴士，12 noon 报告（本周一至周二）
        # 周五：8am 贴士，12 noon 报告（本周一至周四）
        # 注意：每天8点的模板消息已移至 daily_template_curl.py

        # 周一、周三、周五 8点：发送运动贴士
        def exercise_tip_batch():
            log_to_file("💡 [任务执行] 开始发送运动贴士...")
            patients = self.get_patients_from_api()
            log_to_file(f"💡 [任务执行] 找到 {len(patients)} 个患者，准备发送运动贴士")
            sent_count = 0
            for p in patients:
                try:
                    patient_name = p.get('full_name') or p.get('patient_id') or 'Unknown'
                    log_to_file(f"💡 [任务执行] 正在发送运动贴士给患者: {patient_name}")
                    self.send_exercise_tip(p)
                    sent_count += 1
                    log_to_file(f"💡 [任务执行] ✅ 患者 {patient_name} 的运动贴士已发送 (第 {sent_count}/{len(patients)} 个)")
                except Exception as e:
                    log_to_file(f"⚠️ [任务执行] 运动贴士发送异常: {e}")
                time.sleep(1)
            log_to_file(f"💡 [任务执行完成] 运动贴士发送完毕，共发送给 {sent_count}/{len(patients)} 个患者")

        schedule.every().monday.at("08:00").do(exercise_tip_batch)
        schedule.every().wednesday.at("08:00").do(exercise_tip_batch)
        schedule.every().friday.at("08:00").do(exercise_tip_batch)

        # 周一、周三、周五 8点：发送同步手环提醒
        def sync_tracker_batch():
            log_to_file("🛰️ [任务执行] 开始发送同步手环提醒...")
            patients = self.get_patients_from_api()
            log_to_file(f"🛰️ [任务执行] 找到 {len(patients)} 个患者，准备发送同步提醒")
            sent_count = 0
            for p in patients:
                try:
                    patient_name = p.get('full_name') or p.get('patient_id') or 'Unknown'
                    log_to_file(f"🛰️ [任务执行] 正在发送同步提醒给患者: {patient_name}")
                    self.send_sync_tracker_reminder(p)
                    sent_count += 1
                    log_to_file(f"🛰️ [任务执行] ✅ 患者 {patient_name} 的同步提醒已发送 (第 {sent_count}/{len(patients)} 个)")
                except Exception as e:
                    log_to_file(f"⚠️ [任务执行] 同步提醒异常: {e}")
                time.sleep(1)
            log_to_file(f"🛰️ [任务执行完成] 同步提醒发送完毕，共发送给 {sent_count}/{len(patients)} 个患者")

        schedule.every().monday.at("08:00").do(sync_tracker_batch)
        schedule.every().wednesday.at("08:00").do(sync_tracker_batch)
        schedule.every().friday.at("08:00").do(sync_tracker_batch)

        # 周二、周四 8点：发送阻力训练提醒
        def resistance_batch():
            log_to_file("💪 [任务执行] 开始发送阻力训练提醒...")
            patients = self.get_patients_from_api()
            log_to_file(f"💪 [任务执行] 找到 {len(patients)} 个患者，准备发送阻力提醒")
            sent_count = 0
            for p in patients:
                try:
                    patient_name = p.get('full_name') or p.get('patient_id') or 'Unknown'
                    log_to_file(f"💪 [任务执行] 正在发送阻力提醒给患者: {patient_name}")
                    self.send_resistance_reminder(p)
                    sent_count += 1
                    log_to_file(f"💪 [任务执行] ✅ 患者 {patient_name} 的阻力提醒已发送 (第 {sent_count}/{len(patients)} 个)")
                except Exception as e:
                    log_to_file(f"⚠️ [任务执行] 阻力提醒异常: {e}")
                time.sleep(1)
            log_to_file(f"💪 [任务执行完成] 阻力提醒发送完毕，共发送给 {sent_count}/{len(patients)} 个患者")

        schedule.every().tuesday.at("08:00").do(resistance_batch)
        schedule.every().thursday.at("08:00").do(resistance_batch)

        # 周一 12点：发送上周一至周日的运动报告
        def monday_report_batch():
            log_to_file("📊 [任务执行] 开始发送周一运动报告（上周一至周日）...")
            patients = self.get_patients_from_api()
            log_to_file(f"📊 [任务执行] 找到 {len(patients)} 个患者，准备发送周一报告")
            sent_count = 0
            for p in patients:
                try:
                    patient_name = p.get('full_name') or p.get('patient_id') or 'Unknown'
                    log_to_file(f"📊 [任务执行] 正在发送周一报告给患者: {patient_name}")
                    self.send_weekly_summary_and_adjust(p)
                    sent_count += 1
                    log_to_file(f"📊 [任务执行] ✅ 患者 {patient_name} 的周一报告已发送 (第 {sent_count}/{len(patients)} 个)")
                except Exception as e:
                    log_to_file(f"⚠️ [任务执行] 周一报告发送异常: {e}")
                time.sleep(1)
            log_to_file(f"📊 [任务执行完成] 周一报告发送完毕，共发送给 {sent_count}/{len(patients)} 个患者")

        schedule.every().monday.at("12:00").do(monday_report_batch)

        # 周三 12点：发送本周一至周二的运动报告
        def wednesday_report_batch():
            log_to_file("📈 [任务执行] 开始发送周三运动报告（本周一至周二）...")
            patients = self.get_patients_from_api()
            log_to_file(f"📈 [任务执行] 找到 {len(patients)} 个患者，准备发送周三报告")
            sent_count = 0
            for p in patients:
                try:
                    patient_name = p.get('full_name') or p.get('patient_id') or 'Unknown'
                    log_to_file(f"📈 [任务执行] 正在发送周三报告给患者: {patient_name}")
                    self.send_midweek_summary(p, 'mon_tue')
                    sent_count += 1
                    log_to_file(f"📈 [任务执行] ✅ 患者 {patient_name} 的周三报告已发送 (第 {sent_count}/{len(patients)} 个)")
                except Exception as e:
                    log_to_file(f"⚠️ [任务执行] 周三报告发送异常: {e}")
                time.sleep(1)
            log_to_file(f"📈 [任务执行完成] 周三报告发送完毕，共发送给 {sent_count}/{len(patients)} 个患者")

        schedule.every().wednesday.at("12:00").do(wednesday_report_batch)

        # 周五 12点：发送本周一至周四的运动报告
        def friday_report_batch():
            log_to_file("📈 [任务执行] 开始发送周五运动报告（本周一至周四）...")
            patients = self.get_patients_from_api()
            log_to_file(f"📈 [任务执行] 找到 {len(patients)} 个患者，准备发送周五报告")
            sent_count = 0
            for p in patients:
                try:
                    patient_name = p.get('full_name') or p.get('patient_id') or 'Unknown'
                    log_to_file(f"📈 [任务执行] 正在发送周五报告给患者: {patient_name}")
                    self.send_midweek_summary(p, 'mon_thu')
                    sent_count += 1
                    log_to_file(f"📈 [任务执行] ✅ 患者 {patient_name} 的周五报告已发送 (第 {sent_count}/{len(patients)} 个)")
                except Exception as e:
                    log_to_file(f"⚠️ [任务执行] 周五报告发送异常: {e}")
                time.sleep(1)
            log_to_file(f"📈 [任务执行完成] 周五报告发送完毕，共发送给 {sent_count}/{len(patients)} 个患者")

        schedule.every().friday.at("12:00").do(friday_report_batch)

        # ✅ 验证：检查注册的任务数量
        total_jobs = len(schedule.jobs)
        expected_jobs = 11  # 周一/三/五各1个贴士 + 周一/三/五各1个同步提醒 + 周二/四各1个阻力 + 周一/三/五各1个报告（每天模板消息已移至 daily_template_curl.py）
        
        # 先详细列出所有注册的任务（按注册顺序）- 这个最重要，显示实际注册的任务
        log_to_file("=" * 70)
        log_to_file("📋 已注册的任务详情（按注册顺序，这是实际注册的任务）：")
        for i, job in enumerate(schedule.jobs, 1):
            job_name = job.job_func.__name__
            next_run = job.next_run.strftime('%Y-%m-%d %H:%M:%S') if job.next_run else 'N/A'
            # 尝试从job对象中获取更多信息
            job_tag = getattr(job, 'tag', '')
            log_to_file(f"   任务 {i}: {job_name} - 下次运行: {next_run} {job_tag}")
        log_to_file("=" * 70)
        
        log_to_file(f"✅ 验证：共注册了 {total_jobs} 个定时任务（应该正好是 {expected_jobs} 个）")
        
        if total_jobs != expected_jobs:
            log_to_file(f"⚠️ 警告：任务数量异常！应该是 {expected_jobs} 个，实际是 {total_jobs} 个")
        
        # 预期的任务列表（用于参考）
        print("✅ 定时任务已设置完成!")
        print("📋 预期任务列表:")
        print("  - 周一 08:00 发送运动贴士")
        print("  - 周一 08:00 发送同步手环提醒")
        print("  - 周一 12:00 发送运动报告（上周一至周日）")
        print("  - 周二 08:00 发送阻力训练提醒")
        print("  - 周三 08:00 发送运动贴士")
        print("  - 周三 08:00 发送同步手环提醒")
        print("  - 周三 12:00 发送运动报告（本周一至周二）")
        print("  - 周四 08:00 发送阻力训练提醒")
        print("  - 周五 08:00 发送运动贴士")
        print("  - 周五 08:00 发送同步手环提醒")
        print("  - 周五 12:00 发送运动报告（本周一至周四）")
        print("  (注意：每天8点的模板消息由 daily_template_curl.py 处理)")
        print("🚀 正式模式：发送给所有患者")
        

        
        log_to_file("✅ 定时任务已设置 (新加坡时间 SGT):")
        log_to_file("  📋 预期任务列表（参考）：")
        log_to_file("    [1] 周一 08:00 发送运动贴士")
        log_to_file("    [2] 周一 08:00 发送同步手环提醒")
        log_to_file("    [3] 周一 12:00 发送运动报告（上周一至周日）")
        log_to_file("    [4] 周二 08:00 发送阻力训练提醒")
        log_to_file("    [5] 周三 08:00 发送运动贴士")
        log_to_file("    [6] 周三 08:00 发送同步手环提醒")
        log_to_file("    [7] 周三 12:00 发送运动报告（本周一至周二）")
        log_to_file("    [8] 周四 08:00 发送阻力训练提醒")
        log_to_file("    [9] 周五 08:00 发送运动贴士")
        log_to_file("    [10] 周五 08:00 发送同步手环提醒")
        log_to_file("    [11] 周五 12:00 发送运动报告（本周一至周四）")
        log_to_file("  (注意：每天8点的模板消息由 daily_template_curl.py 处理)")
        log_to_file("🚀 正式模式：发送给所有患者")
        
        # 运行调度器
        log_to_file("🔄 开始运行调度器循环...")
        loop_count = 0
        while True:
            loop_count += 1
            current_time = datetime.now(self.sgt)
            log_to_file(f"⏰ 第{loop_count}次检查 - 当前SGT时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 检查是否有待执行的任务
            pending_jobs = [job for job in schedule.jobs if job.should_run]
            if pending_jobs:
                log_to_file(f"📋 发现 {len(pending_jobs)} 个待执行任务:")
                for job in pending_jobs:
                    job_name = job.job_func.__name__
                    next_run_str = job.next_run.strftime('%Y-%m-%d %H:%M:%S') if job.next_run else 'N/A'
                    log_to_file(f"   - {job_name} (下次运行: {next_run_str})")
                log_to_file(f"🚀 开始执行待执行任务...")
            
            # 执行待执行的任务
            # 注意：schedule.run_pending() 返回 None，不返回执行的任务数量
            if pending_jobs:
                log_to_file(f"🚀 开始执行 {len(pending_jobs)} 个待执行任务...")
            schedule.run_pending()
            if pending_jobs:
                log_to_file(f"✅ 已尝试执行 {len(pending_jobs)} 个任务（schedule.run_pending() 已完成）")
            
            # 记录所有任务的下次运行时间（用于调试）
            if loop_count % 60 == 0:  # 每小时记录一次所有任务的 next_run
                log_to_file(f"📅 所有任务的下次运行时间:")
                for i, job in enumerate(schedule.jobs, 1):
                    job_name = job.job_func.__name__
                    next_run_str = job.next_run.strftime('%Y-%m-%d %H:%M:%S') if job.next_run else 'N/A'
                    log_to_file(f"   任务 {i}: {job_name} -> {next_run_str}")
            log_to_file(f"💤 等待60秒后进行下次检查...")
            time.sleep(60)  # 每分钟检查一次
            
if __name__ == "__main__":
    log_to_file("=" * 50)
    log_to_file("🤖 WhatsApp定时提醒服务启动中...")
    log_to_file("=" * 50)

    scheduler = WhatsAppScheduler()
    scheduler.start_scheduler()
