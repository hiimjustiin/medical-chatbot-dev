import { Controller, Post, Body, Res } from '@nestjs/common';
import { ChatService } from './gpt.service';
import { Response } from 'express';

@Controller('chat')
export class ChatController {
  constructor(private readonly chatService: ChatService) {}

  @Post('message')
  async GPTResponse(@Body() body: any, @Res() res: Response) {
    const phone = body.From?.replace('whatsapp:', '').trim();
    const message = body.Body?.trim();

    console.log('Incoming Twilio body:', body);
    console.log('Parsed phone:', phone);
    console.log('Parsed message:', message);

    if (!phone || !message) {
      return res.status(400).send('<Response><Message>Missing phone or message content.</Message></Response>');
    }

    const result = await this.chatService.chatWithGPT(phone, message);

    const twiml = `<Response><Message>${result.response}</Message></Response>`;
    res.set('Content-Type', 'text/xml');
    res.status(200).send(twiml);
  }
}
