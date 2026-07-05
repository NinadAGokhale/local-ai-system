# Saratthya Dashboard - TODO List

## Status: Local Models Working ✅
Both Ollama and MLX models are confirmed working via API tests:
- Ollama: `curl -X POST http://127.0.0.1:5002/api/chat -d '{"message":"hi","model":"ollama/llama3.2:3b"}'` ✅
- MLX: `curl -X POST http://127.0.0.1:5002/api/chat -d '{"message":"hi","model":"mlx/Llama-3.2-3B-Instruct-4bit"}'` ✅

If you're experiencing issues, check:
1. **Response time**: Local models can take 10-30 seconds. Check browser console for timeouts.
2. **Model selection**: Verify the model dropdown shows Ollama/MLX tabs and models are listed.
3. **Browser console**: Open DevTools (F12) and check for JavaScript errors.
4. **Network tab**: Check if `/api/models` returns the correct model list.

## High Priority

### 1. UI Beautification (Next Agent Task)
**Goal**: Make the dashboard visually appealing and intuitive for non-technical users.

#### Persona Prominence
- [ ] Make persona chip larger and more visually distinct (different color, icon, or dedicated section)
- [ ] Add persona avatar/icon next to messages when persona is active
- [ ] Show persona description in tooltip when hovering over chip
- [ ] Add visual indicator when persona is active (e.g., colored border around chat area)

#### Empty State Hero
- [ ] Better onboarding screen when no messages
- [ ] Show example prompts with persona/agent combinations
- [ ] Persona showcase carousel (click to see each persona's style)
- [ ] Agent/skill quick-start guide with visual cards

#### Message Avatars
- [ ] Add small avatar icons for different personas:
  - 🎭 Miranda Priestly (pink)
  - 💼 Marc Andreessen (orange)
  - 🦉 Warren Buffett (gold)
  - ⚽ José Mourinho (red)
  - 💪 The Rock (yellow)
- [ ] Add agent avatars (👨‍💻 CTO, 📈 Growth, 🎨 Designer, etc.)
- [ ] Show avatar in message bubbles

#### Sidebar Improvements
- [ ] Group conversations by date (Today, Yesterday, This Week, Older)
- [ ] Add search/filter for conversations
- [ ] Show message count or last message preview
- [ ] Add "Archive" feature for old conversations
- [ ] Drag-and-drop to reorder pinned conversations

#### Provider Tab Animations
- [ ] Smooth transitions when switching providers
- [ ] Loading spinners when fetching models
- [ ] Better visual feedback for "down" state (red pulse animation)
- [ ] Tooltip showing server status details

#### Chat Header Polish
- [ ] Make rename icon (✎) more obvious with hover animation
- [ ] Add subtle background highlight when persona/agent active
- [ ] Show active persona/agent in header with icons
- [ ] Add "Clear all" button to reset persona/agent/skills

#### Conversation List Legibility
- [ ] Better truncation for long titles (show full title on hover)
- [ ] Show pin icon (📍) more prominently
- [ ] Add hover states for rename/pin actions
- [ ] Show last message timestamp
- [ ] Add "unread" indicator for new messages

#### Smooth Animations
- [ ] CSS transitions for sidebar collapse/expand
- [ ] Fade-in for mode bar chip additions/removals
- [ ] Popup fade-ins for persona picker
- [ ] Smooth scroll for message list
- [ ] Loading skeleton for async operations

#### Typography Hierarchy
- [ ] Better font sizes/weights for headers
- [ ] Distinguish user vs bot messages with font weight
- [ ] Better spacing for code blocks
- [ ] Improve metadata font (timestamps, model names)

#### Color Coding
- [ ] Different accent colors for providers:
  - Ollama: Blue (#3b82f6)
  - MLX: Green (#10b981)
  - Cloud: Purple (#8b5cf6)
- [ ] Persona colors:
  - Miranda: Pink (#ec4899)
  - Marc: Orange (#f97316)
  - Warren: Gold (#eab308)
  - José: Red (#ef4444)
  - Rock: Yellow (#facc15)
- [ ] Use colors consistently across UI

#### Icons Consistency
- [ ] Use consistent icon set throughout (emoji or SVG)
- [ ] Sidebar icons, mode bar icons, button icons
- [ ] Empty state icons
- [ ] Loading spinner icons

#### Mobile Polish
- [ ] Larger touch targets (min 44x44px)
- [ ] Swipe-to-delete conversations
- [ ] Pull-to-refresh for conversation list
- [ ] Better keyboard handling (auto-resize textarea)
- [ ] Test on Safari and Chrome mobile

#### Loading States
- [ ] Skeleton screens for loading conversations
- [ ] Skeleton screens for fetching models
- [ ] "Sending..." indicator for messages
- [ ] Progress indicator for long-running operations

#### Error States
- [ ] Better error messages with retry buttons
- [ ] Offline detection with banner
- [ ] Graceful degradation when servers are down
- [ ] User-friendly error messages (not technical jargon)

#### Accessibility
- [ ] Better contrast ratios (WCAG AA compliance)
- [ ] Focus states for keyboard navigation
- [ ] ARIA labels for screen readers
- [ ] Skip-to-content link
- [ ] Test with screen reader (VoiceOver/NVDA)

#### Dark Mode Refinement
- [ ] Better color palette for dark mode
- [ ] Ensure all elements have sufficient contrast
- [ ] Test all components in dark mode
- [ ] Add smooth transition between themes

#### Catalogue Modal
- [ ] Better visual design for agent/skill/persona browser
- [ ] Cards with descriptions and icons
- [ ] Search functionality
- [ ] Filters (by category, by popularity)
- [ ] "Favorites" feature

#### Message Formatting
- [ ] Better markdown rendering
- [ ] Code syntax highlighting (Prism.js or highlight.js)
- [ ] Copy buttons for code blocks
- [ ] Expandable code blocks for long code
- [ ] Better table rendering

#### Typing Indicator
- [ ] Show "Saratthya is thinking..." with animation
- [ ] Persona-specific typing animations
- [ ] Show which model is processing
- [ ] Estimated time remaining (if possible)

#### Sound Effects (Optional)
- [ ] Subtle sounds for message send/receive
- [ ] Toggle in settings
- [ ] Different sounds for different personas (optional)

### 2. Fix NPort Tunnel DNS Behind Surfshark VPN
**Issue**: `lookup region1.v2.argotunnel.com: i/o timeout` caused by Surfshark WireGuard DNS.

**Current Status**: `TUNNEL_DNS_RESOLVER_ADDRS=1.1.1.1:53` set in plist but tunnel still fails.

**Tasks**:
- [ ] Investigate if Surfshark is blocking QUIC protocol
- [ ] Try forcing HTTP/2 instead of QUIC: `TUNNEL_TRANSPORT_PROTOCOL=http2`
- [ ] Test with different DNS resolvers: `8.8.8.8:53`, `9.9.9.9:53`
- [ ] Check if macOS DNS cache needs flush: `sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder`
- [ ] Consider alternative tunnel solution (ngrok, localtunnel)
- [ ] Document workaround in README

### 3. Test Persona + Agent + Skills Stacking
**Goal**: Verify that persona, agent, and skills can all be active simultaneously and produce correct output.

**Test Cases**:
- [ ] Persona only: Set persona, send message, verify voice matches
- [ ] Agent only: Set agent, send message, verify task execution
- [ ] Persona + Agent: Set both, verify persona voice + agent task execution
- [ ] Persona + Agent + Skills: Set all three, verify hierarchical prompt construction
- [ ] Switch conversations: Verify persona/agent/skills persist correctly
- [ ] Clear persona: Verify agent/skills remain active
- [ ] Clear agent: Verify persona/skills remain active

**Expected Behavior**:
- Prompt hierarchy: `[Persona]` → `[Agent]` → `[Active Skills]` → `[User Request]`
- Persona dominates tone, agent dominates task execution
- Skills provide reference material

### 4. Add More Personas Based on User Feedback
**Current Personas**: Miranda Priestly, Marc Andreessen, Warren Buffett, José Mourinho, The Rock

**Potential Additions**:
- [ ] Steve Jobs (visionary, design-focused)
- [ ] Elon Musk (ambitious, first-principles thinking)
- [ ] Oprah Winfrey (empathetic, storytelling)
- [ ] Gordon Ramsay (direct, no-nonsense, culinary)
- [ ] Sherlock Holmes (analytical, deductive reasoning)
- [ ] Yoda (wise, cryptic, mentor)

**Tasks**:
- [ ] Create persona `.md` files in `~/.config/opencode/personas/`
- [ ] Test each persona with sample prompts
- [ ] Add persona descriptions to README
- [ ] Gather user feedback on which personas to add

## Medium Priority

### 5. Verify Conversation Switching End-to-End
**Goal**: Ensure conversation switching works correctly in all scenarios.

**Test Cases**:
- [ ] Switch from unsaved to saved conversation
- [ ] Switch from saved to saved conversation
- [ ] Switch back to previously active conversation
- [ ] Verify history loads correctly
- [ ] Verify persona/agent/skills persist
- [ ] Verify pin/rename persist
- [ ] Verify no duplicate entries created

### 6. Performance Optimization
**Goal**: Improve response times and reduce resource usage.

**Tasks**:
- [ ] Add caching for `/api/models` endpoint (cache for 30 seconds)
- [ ] Add caching for `/api/agents` and `/api/skills` endpoints
- [ ] Optimize `_build_prompt()` to avoid redundant file reads
- [ ] Add connection pooling for Ollama/MLX HTTP requests
- [ ] Consider using async/await for non-blocking I/O
- [ ] Profile slow endpoints with `cProfile`

### 7. Documentation Updates
**Goal**: Ensure all documentation is up-to-date and comprehensive.

**Tasks**:
- [ ] Update README with persona system documentation
- [ ] Add persona creation guide
- [ ] Update architecture diagrams
- [ ] Add troubleshooting section for common issues
- [ ] Document API endpoints with examples
- [ ] Create user guide for non-technical users

### 8. Testing Improvements
**Goal**: Increase test coverage and add integration tests.

**Tasks**:
- [ ] Add tests for persona system
- [ ] Add tests for conversation pin/rename
- [ ] Add integration tests for `/api/chat` endpoint
- [ ] Add tests for model routing (Ollama/MLX/Opencode)
- [ ] Add tests for access request workflow
- [ ] Set up CI/CD pipeline (GitHub Actions)

## Low Priority

### 9. Feature Requests
- [ ] Export conversations as PDF/Markdown
- [ ] Share conversations via link
- [ ] Conversation templates (pre-built prompts)
- [ ] Multi-language support
- [ ] Voice input/output (speech-to-text, text-to-speech)
- [ ] Image generation integration (DALL-E, Stable Diffusion)
- [ ] File upload support (PDF, images, code files)
- [ ] Collaborative editing (multiple users in same conversation)

### 10. Security Hardening
- [ ] Rate limiting for API endpoints
- [ ] Input validation and sanitization
- [ ] CSRF protection
- [ ] Content Security Policy (CSP) headers
- [ ] Regular security audits
- [ ] Dependency vulnerability scanning

### 11. Monitoring and Analytics
- [ ] Add logging for all API requests
- [ ] Track model usage statistics
- [ ] Track persona/agent/skill usage
- [ ] Monitor response times
- [ ] Set up alerts for errors/timeouts
- [ ] Create admin dashboard for analytics

## Notes

### Known Issues
1. **NPort DNS**: Tunnel fails behind Surfshark VPN due to DNS resolution issues
2. **Opencode CLI**: `--agent` flag returns `UnknownError` — using fallback with `--model`
3. **Slow local models**: Ollama/MLX can take 10-30 seconds for complex prompts

### Architecture Decisions
- Persona is a voice layer, agent is a task executor
- One persona at a time, one agent at a time, multiple skills
- Conversation titles are auto-generated from first message unless custom-renamed
- Access requests saved to file + email notification (no database)

### Testing Commands
```bash
# Test Ollama
curl -X POST http://127.0.0.1:5002/api/chat -d '{"message":"hi","model":"ollama/llama3.2:3b"}'

# Test MLX
curl -X POST http://127.0.0.1:5002/api/chat -d '{"message":"hi","model":"mlx/Llama-3.2-3B-Instruct-4bit"}'

# Test Opencode Go
curl -X POST http://127.0.0.1:5002/api/chat -d '{"message":"hi","model":"opencode-go/deepseek-v4-flash"}'

# Test persona
curl -X POST http://127.0.0.1:5002/api/personas -d '{"persona":"the-rock"}'

# Run tests
python3 -m pytest src/tests/test_session_manager.py -v
python3 -m pytest src/tests/test_dashboard.py -v
```

### File Locations
- Personas: `~/.config/opencode/personas/*.md`
- Agents: `~/.config/opencode/agents/*.md`
- Skills: `~/.config/opencode/skills/*/SKILL.md`
- Logs: `logs/flask.stderr.log`, `logs/access_requests.jsonl`
- Sessions: `.sessions.json` (gitignored)
- Secrets: `src/web/.env`, `src/web/.secret_key` (gitignored)
