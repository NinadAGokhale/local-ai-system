const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const { execSync } = require('child_process');
const path = require('path');

const client = new Client({
    authStrategy: new LocalAuth({ dataPath: path.join(__dirname, '.wwebjs_auth') }),
    puppeteer: { headless: true, args: ['--no-sandbox'] }
});

client.on('qr', (qr) => {
    console.log('Scan this QR code with WhatsApp:');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('WhatsApp bridge is ready!');
});

client.on('message', async (msg) => {
    if (msg.from.endsWith('@c.us')) {
        const response = await processCommand(msg.from, msg.body);
        msg.reply(response);
    }
});

async function processCommand(phone, command) {
    try {
        const escaped = command
            .replace(/\\/g, '\\\\')
            .replace(/"/g, '\\"')
            .replace(/`/g, '\\`')
            .replace(/\$/g, '\\$');
        const result = execSync(
            `python3 main.py "${phone}" "${escaped}"`,
            { timeout: 120000, encoding: 'utf-8', cwd: __dirname }
        );
        const lines = result.trim().split('\n');
        return lines.filter(l => !l.includes('> build') && !l.includes('```')).join('\n').trim() || 'Done';
    } catch (err) {
        return `Error: ${err.message}`;
    }
}

client.initialize();
