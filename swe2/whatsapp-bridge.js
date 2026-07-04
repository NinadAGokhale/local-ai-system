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
        const response = await processCommand(msg.body);
        msg.reply(response);
    }
});

async function processCommand(command) {
    try {
        const result = execSync(
            `opencode run --model ollama/qwen2.5-coder:7b "${command.replace(/"/g, '\\"')}"`,
            { timeout: 120000, encoding: 'utf-8', cwd: __dirname }
        );
        return result || 'No output';
    } catch (err) {
        return `Error: ${err.message}`;
    }
}

client.initialize();
