from flask import Blueprint, request, jsonify
from routes.webhook import log_to_file
import re

rules_bp = Blueprint('rules', __name__)


def _normalize_phone(phone: str) -> str:
    clean = re.sub(r'\D', '', phone or '')
    if len(clean) == 8:
        clean = '65' + clean
    return clean


# 每日提醒功能已移除


@rules_bp.route('/weekly', methods=['POST'])
def run_weekly_rules():
    """手动触发：每周总结 + 目标自适应。
    Body 可选参数：patient_id
    """
    data = request.get_json(silent=True) or {}
    target_patient_id = str(data.get('patient_id') or '').strip()

    from scheduler import WhatsAppScheduler
    sched = WhatsAppScheduler()
    patients = []
    if target_patient_id:
        rec = sched.get_patient_record(target_patient_id)
        if not rec:
            return jsonify({"status": "error", "message": "patient not found"}), 404
        patients = [{
            'id': rec.get('id'),
            'patient_id': rec.get('id'),
            'full_name': rec.get('full_name') or rec.get('name') or '用户',
            'phone_number': rec.get('phone_number') or rec.get('phone') or ''
        }]
    else:
        patients = sched.get_patients_from_api() or []

    results = []
    for p in patients:
        try:
            sched.send_weekly_summary_and_adjust(p)
            results.append({"patient": p.get('id') or p.get('patient_id'), "status": "ok"})
        except Exception as e:
            log_to_file(f"❌ weekly rules error: {e}")
            results.append({"patient": p.get('id') or p.get('patient_id'), "status": "error", "error": str(e)})

    return jsonify({"status": "completed", "count": len(results), "results": results}), 200


@rules_bp.route('/resistance', methods=['POST'])
def run_resistance_rules():
    """手动触发：阻力训练提醒（周二/周五标准，但此端点随时可用）。
    Body 可选参数：patient_id
    """
    data = request.get_json(silent=True) or {}
    target_patient_id = str(data.get('patient_id') or '').strip()

    from scheduler import WhatsAppScheduler
    sched = WhatsAppScheduler()
    patients = []
    if target_patient_id:
        rec = sched.get_patient_record(target_patient_id)
        if not rec:
            return jsonify({"status": "error", "message": "patient not found"}), 404
        patients = [{
            'id': rec.get('id'),
            'patient_id': rec.get('id'),
            'full_name': rec.get('full_name') or rec.get('name') or '用户',
            'phone_number': rec.get('phone_number') or rec.get('phone') or ''
        }]
    else:
        patients = sched.get_patients_from_api() or []

    results = []
    for p in patients:
        try:
            sched.send_resistance_reminder(p)
            results.append({"patient": p.get('id') or p.get('patient_id'), "status": "ok"})
        except Exception as e:
            log_to_file(f"❌ resistance rules error: {e}")
            results.append({"patient": p.get('id') or p.get('patient_id'), "status": "error", "error": str(e)})

    return jsonify({"status": "completed", "count": len(results), "results": results}), 200


