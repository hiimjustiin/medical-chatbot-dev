import { Controller, Post, Body, Req, Res } from '@nestjs/common';
import { ChatService } from './gpt.service';
import { Request, Response } from 'express';

@Controller('chat')
export class ChatController {
  constructor(private readonly chatService: ChatService) {}

  @Post('message')
  async GPTResponse(@Body() body: any, @Req() req: Request, @Res() res: Response) {
    const phone = (body.From || body.from || '').replace('whatsapp:', '').trim();
    const message = (body.Body || body.body || '').trim();

    console.log('Incoming body:', body);
    console.log('Parsed phone:', phone);
    console.log('Parsed message:', message);

    if (!phone || !message) {
      const fallbackXML = `<Response><Message>Missing phone or message content.</Message></Response>`;
      res.set('Content-Type', 'text/xml');
      return res.status(400).send(fallbackXML);
    }

    const result = await this.chatService.chatWithGPT(phone, message);

    // ✅ Flask 转发过来的请求 → 返回 JSON
    if (req.headers['content-type']?.includes('application/json')) {
      return res.status(200).json(result);
    }

    // ✅ Twilio 的 webhook → 返回 XML
    const twiml = `<Response><Message>${result.response}</Message></Response>`;
    res.set('Content-Type', 'text/xml');
    return res.status(200).send(twiml);
  }
}

