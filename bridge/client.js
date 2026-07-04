const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const OUTBOX_FILE = path.join(ROOT, 'outbox.jsonl');

const client = new Client({
    authStrategy: new LocalAuth({ dataPath: path.join(ROOT, '.wwebjs_auth') }),
    puppeteer: { headless: true, args: ['--no-sandbox'] }
});

client.on('qr', (qr) => {
    console.log('========================================');
    console.log(' SCAN THIS QR CODE WITH WHATSAPP');
    console.log(' Open WhatsApp → Linked Devices → Link');
    console.log('========================================');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('✓ WhatsApp bridge connected!');
    console.log('  Your WhatsApp number is now the bot.');
    console.log('  Send messages to your own number to test.');
    pollOutbox();
});

client.on('message', async (msg) => {
    if (msg.from.endsWith('@c.us') && !msg.from.includes('status@broadcast')) {
        console.log(`\n📩 Incoming: ${msg.from} → ${msg.body.slice(60)}`);
        const response = await processCommand(msg.from, msg.body);
        msg.reply(response);
        console.log(`📤 Replied: ${response.slice(80)}`);
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
            { timeout: 120000, encoding: 'utf-8', cwd: ROOT }
        );
        const lines = result.trim().split('\n');
        return lines.filter(l => !l.includes('> build')).join('\n').trim() || 'Done';
    } catch (err) {
        console.error('Error processing command:', err.message);
        return `Error: ${err.message}`;
    }
}

async function pollOutbox() {
    setInterval(async () => {
        try {
            if (!fs.existsSync(OUTBOX_FILE)) return;
            const data = fs.readFileSync(OUTBOX_FILE, 'utf-8').trim();
            if (!data) return;

            const lines = data.split('\n').filter(Boolean);
            const unsent = [];

            for (const line of lines) {
                try {
                    const entry = JSON.parse(line);
                    if (!entry.sent && entry.phone) {
                        await client.sendMessage(entry.phone, entry.message);
                        console.log(`📤 Outbox sent to ${entry.phone}`);
                    }
                    unsent.push(false); // mark as sent
                } catch (e) {
                    unsent.push(true); // keep as unsent
                }
            }

            // Rewrite file with only unsent entries
            const remaining = lines.filter((l, i) => {
                try {
                    const entry = JSON.parse(l);
                    return entry.sent === false && unsent[i] === true;
                } catch { return false; }
            });
            fs.writeFileSync(OUTBOX_FILE, remaining.join('\n') + (remaining.length ? '\n' : ''));
        } catch (err) {
            // File might be in use, skip
        }
    }, 2000); // poll every 2 seconds
}

client.initialize();
