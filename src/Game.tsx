import React, { useEffect, useRef, useState } from 'react';
import { getQuestions } from './questions';

const WIDTH = 1000;
const HEIGHT = 600;
const GRAVITY = 0.8;
const WORLD_WIDTH = 5000;
const GROUND_Y = 500;
const TOTAL_QUESTIONS = 10;
const MAX_LEVEL = 10;
const BLOCK_SPACING = 450;
const TIME_TO_START = 3.0;
const TIME_TO_FINISH = 7.0;

// Colors
const BLACK = '#141414';
const WHITE = '#ffffff';
const RED = '#dc3232';
const GOLD = '#ffc800';
const GREEN = '#32be46';
const DARK_BROWN = '#643c1e';
const PIPE_GREEN = '#32a032';
const PIPE_DARK = '#1e641e';
const TRUMP_SKIN = '#ffb964';
const TRUMP_HAIR = '#ffd232';
const TRUMP_SUIT = '#1e3264';

interface Block {
  rect: { x: number, y: number, w: number, h: number };
  question: string;
  answers: string[];
  done: boolean;
  level: number;
}

interface ScoreEntry {
  name: string;
  email: string;
  date: string;
  time?: number;
  score?: number;
}

export default function Game() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // HUD states for React
  const [gameState, setGameState] = useState<'name_entry' | 'highscores' | 'playing' | 'question' | 'dying' | 'winner'>('name_entry');
  const [, setTick] = useState(0); // force re-render

  const s = useRef({
    state: 'name_entry' as 'name_entry' | 'highscores' | 'playing' | 'question' | 'dying' | 'winner',
    playerName: "",
    playerEmail: "",
    nameFieldActive: true,
    score: 0,
    message: "",
    rageLine1: "",
    rageLine2: "",
    deathTimer: 0,
    fadeAlpha: 0,
    ghostYOffset: 0,
    deathAnimationDone: false,
    
    player: { x: 80, y: 345, vx: 0, vy: 0, facing: 1, walkFrame: 0, onGround: false },
    blocks: [] as Block[],
    currentBlock: null as Block | null,
    cameraX: 0,
    
    inputText: "",
    gameStartTime: 0,
    questionStartTime: 0,
    typingStartTime: 0,
    hasStartedTyping: false,
    finishTime: 0,
    
    keys: {} as Record<string, boolean>
  }).current;

  const audioRef = useRef({
    bgMusic: null as HTMLAudioElement | null,
    deathSound: null as HTMLAudioElement | null,
    musicStarted: false
  }).current;

  const imgRef = useRef({
    trumpRight: null as HTMLImageElement | null,
    trumpRage: null as HTMLImageElement | null,
    background: null as HTMLImageElement | null,
    block: null as HTMLImageElement | null,
    ground: null as HTMLImageElement | null,
  }).current;

  const buildGame = () => {
    const blocks: Block[] = [];
    let x = 400;
    for (let i = 0; i < TOTAL_QUESTIONS; i++) {
      const level = Math.min(i + 1, MAX_LEVEL);
      const qPool = getQuestions(level);
      const used = blocks.map(b => b.question);
      let q = qPool.find(item => !used.includes(item[0]));
      if (!q) q = qPool[0];
      
      blocks.push({
        rect: { x, y: 345, w: 70, h: 70 },
        question: q[0],
        answers: q[1],
        done: false,
        level
      });
      x += BLOCK_SPACING;
    }
    return blocks;
  };

  const getScores = () => {
    try {
      const data = localStorage.getItem("highscores");
      if (data) return JSON.parse(data);
    } catch {}
    return { winners: [], best_scores: [] };
  };

  const addScore = (name: string, email: string, correctCount: number, finishTime?: number) => {
    const scores = getScores();
    const entry: ScoreEntry = {
      name, email,
      date: new Date().toLocaleString('is-IS', { dateStyle: 'short', timeStyle: 'short' })
    };
    
    if (finishTime !== undefined) {
      entry.time = finishTime;
      scores.winners.push(entry);
      scores.winners.sort((a: any, b: any) => a.time - b.time);
      scores.winners = scores.winners.slice(0, 10);
    } else {
      entry.score = correctCount;
      scores.best_scores.push(entry);
      scores.best_scores.sort((a: any, b: any) => b.score - a.score);
      scores.best_scores = scores.best_scores.slice(0, 10);
    }
    localStorage.setItem("highscores", JSON.stringify(scores));
  };

  const triggerDeath = (timeout: boolean) => {
    const name = s.playerName.toUpperCase() || "LOSER";
    if (timeout) {
      s.rageLine1 = \`TOO SLOW, \${name}! RIGGED!\`;
      s.rageLine2 = "You couldn't even type in time. Sad!";
    } else {
      const messages = [
        [\`WRONG, \${name}! TOTAL DISASTER!\`, "Nobody fails worse than you, believe me!"],
        [\`FAKE ANSWER, \${name}! SAD!\`, "Back to the beginning, loser!"],
        [\`\${name}, YOU'RE FIRED!\`, "That was the worst answer I've ever seen!"],
        [\`TOTAL LOSER, \${name}!\`, "Go back to start, okay? Just go back!"],
        [\`TREMENDOUS FAILURE, \${name}!\`, "Nobody fails bigger than you, nobody!"]
      ];
      const r = messages[Math.floor(Math.random() * messages.length)];
      s.rageLine1 = r[0];
      s.rageLine2 = r[1];
    }
    
    s.inputText = "";
    s.state = 'dying';
    s.ghostYOffset = 0;
    s.fadeAlpha = 0;
    s.deathTimer = 0;
    s.deathAnimationDone = false;
    setGameState('dying');
    
    if (audioRef.bgMusic) audioRef.bgMusic.pause();
    if (audioRef.deathSound) {
      audioRef.deathSound.currentTime = 0;
      audioRef.deathSound.play().catch(() => {});
    }
  };

  useEffect(() => {
    // Load images
    const loadImg = (src: string) => {
      const i = new Image();
      i.src = src;
      return i;
    };
    imgRef.trumpRight = loadImg("/trump1-bg.png");
    imgRef.trumpRage = loadImg("/trumprage.png");
    imgRef.background = loadImg("/bakgrunnur1.png");
    imgRef.block = loadImg("/kubbur.png");
    imgRef.ground = loadImg("/jord1.png");

    // Load Audio
    audioRef.bgMusic = new Audio("/bg_music.wav");
    audioRef.bgMusic.loop = true;
    audioRef.bgMusic.volume = 0.5;
    audioRef.deathSound = new Audio("/death_sound.wav");
    audioRef.deathSound.volume = 0.8;

    s.blocks = buildGame();

    const playMusic = () => {
      if (!audioRef.musicStarted && audioRef.bgMusic) {
        audioRef.bgMusic.play().catch(() => {});
        audioRef.musicStarted = true;
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      playMusic();
      s.keys[e.key] = true;
      const now = performance.now() / 1000;

      if (s.state === 'name_entry') {
        if (e.key === 'Tab') {
          e.preventDefault();
          s.nameFieldActive = !s.nameFieldActive;
        } else if (e.key === 'Enter') {
          if (s.playerName.trim() && s.playerEmail.trim()) {
            s.state = 'playing';
            s.gameStartTime = now;
            s.blocks = buildGame();
            s.player.x = 80;
            s.player.y = 345;
            s.player.vx = 0;
            s.player.vy = 0;
            s.score = 0;
            setGameState('playing');
          }
        } else if (e.key.toLowerCase() === 'h' && s.playerName.length === 0) {
          s.state = 'highscores';
          setGameState('highscores');
        } else if (e.key === 'Backspace') {
          if (s.nameFieldActive) s.playerName = s.playerName.slice(0, -1);
          else s.playerEmail = s.playerEmail.slice(0, -1);
        } else if (e.key.length === 1 && e.key.match(/^[a-zA-Z0-9_@. -]$/)) {
          if (s.nameFieldActive && s.playerName.length < 16) s.playerName += e.key;
          else if (!s.nameFieldActive && s.playerEmail.length < 40) s.playerEmail += e.key;
        }
        setTick(t => t + 1);
      } 
      else if (s.state === 'highscores') {
        if (e.key === ' ') {
          s.state = 'name_entry';
          setGameState('name_entry');
        }
      }
      else if (s.state === 'question') {
        e.preventDefault();
        if (e.key === 'Enter') {
          if (s.inputText.trim()) {
            const isCorrect = s.currentBlock?.answers.some(
              ans => ans.toLowerCase().trim() === s.inputText.toLowerCase().trim()
            );
            if (isCorrect) {
              s.score++;
              s.message = \`Rétt, \${s.playerName}! \${s.score}/\${TOTAL_QUESTIONS}\`;
              if (s.currentBlock) s.currentBlock.done = true;
              s.inputText = "";
              s.state = 'playing';
              s.player.x += 90;
              setGameState('playing');
            } else {
              addScore(s.playerName, s.playerEmail, s.score);
              triggerDeath(false);
            }
          }
        } else if (e.key === 'Backspace') {
          s.inputText = s.inputText.slice(0, -1);
        } else if (e.key.length === 1) {
          if (s.inputText.length < 30) {
            if (!s.hasStartedTyping && e.key.trim()) {
              s.hasStartedTyping = true;
              s.typingStartTime = now;
            }
            s.inputText += e.key;
          }
        }
        setTick(t => t + 1);
      }
      else if (s.state === 'dying' && s.deathAnimationDone) {
        if (e.key === ' ') {
          s.blocks = buildGame();
          s.player.x = 80; s.player.y = 345;
          s.player.vx = 0; s.player.vy = 0;
          s.score = 0;
          s.gameStartTime = now;
          s.state = 'playing';
          s.fadeAlpha = 0;
          s.ghostYOffset = 0;
          s.message = "";
          setGameState('playing');
          if (audioRef.bgMusic) {
            audioRef.bgMusic.currentTime = 0;
            audioRef.bgMusic.play().catch(()=>{});
          }
        }
      }
      else if (s.state === 'winner') {
        if (e.key === ' ') {
          s.state = 'highscores';
          setGameState('highscores');
        } else if (e.key.toLowerCase() === 'r') {
          s.blocks = buildGame();
          s.player.x = 80; s.player.y = 345;
          s.player.vx = 0; s.player.vy = 0;
          s.score = 0;
          s.gameStartTime = now;
          s.state = 'playing';
          s.message = "";
          setGameState('playing');
          if (audioRef.bgMusic) {
            audioRef.bgMusic.currentTime = 0;
            audioRef.bgMusic.play().catch(()=>{});
          }
        }
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      s.keys[e.key] = false;
    };

    window.addEventListener('keydown', handleKeyDown, { passive: false });
    window.addEventListener('keyup', handleKeyUp);

    let animationId: number;
    const loop = () => {
      update();
      draw();
      animationId = requestAnimationFrame(loop);
    };
    loop();

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
      cancelAnimationFrame(animationId);
      if (audioRef.bgMusic) audioRef.bgMusic.pause();
    };
  }, []);

  const update = () => {
    const now = performance.now() / 1000;
    
    if (s.state === 'question') {
      if (!s.hasStartedTyping) {
        if (now - s.questionStartTime >= TIME_TO_START) {
          addScore(s.playerName, s.playerEmail, s.score);
          triggerDeath(true);
        }
      } else {
        if (now - s.typingStartTime >= TIME_TO_FINISH) {
          addScore(s.playerName, s.playerEmail, s.score);
          triggerDeath(true);
        }
      }
    }

    if (s.state === 'dying' && !s.deathAnimationDone) {
      s.deathTimer++;
      if (s.deathTimer < 80) {
        s.ghostYOffset -= 3;
      } else if (s.deathTimer < 140) {
        s.fadeAlpha = Math.min(1, (s.deathTimer - 80) / 60);
      } else if (s.deathTimer >= 160) {
        s.deathAnimationDone = true;
        s.fadeAlpha = 1;
        setTick(t => t+1); // force update react UI
      }
    }

    if (s.state === 'playing') {
      s.player.vx = 0;
      if (s.keys['a'] || s.keys['ArrowLeft']) {
        s.player.vx = -5; s.player.facing = -1; s.player.walkFrame++;
      }
      if (s.keys['d'] || s.keys['ArrowRight']) {
        s.player.vx = 5; s.player.facing = 1; s.player.walkFrame++;
      }
      if ((s.keys['w'] || s.keys[' '] || s.keys['ArrowUp']) && s.player.onGround) {
        s.player.vy = -16; s.player.onGround = false;
      }

      s.player.vy += GRAVITY;
      s.player.x += s.player.vx;
      s.player.y += s.player.vy;

      if (s.player.y + 155 >= GROUND_Y) {
        s.player.y = GROUND_Y - 155;
        s.player.vy = 0;
        s.player.onGround = true;
      }

      s.player.x = Math.max(0, Math.min(s.player.x, WORLD_WIDTH - 80));

      const pRect = { x: s.player.x, y: s.player.y, w: 80, h: 155 };
      for (const b of s.blocks) {
        if (!b.done && pRect.x < b.rect.x + b.rect.w && pRect.x + pRect.w > b.rect.x &&
            pRect.y < b.rect.y + b.rect.h && pRect.y + pRect.h > b.rect.y) {
            
            s.currentBlock = b;
            s.inputText = "";
            s.questionStartTime = now;
            s.hasStartedTyping = false;
            s.typingStartTime = 0;
            s.player.x = b.rect.x - pRect.w;
            s.player.vx = 0;
            s.state = 'question';
            setGameState('question');
        }
      }

      if (s.score >= TOTAL_QUESTIONS) {
        s.finishTime = now - s.gameStartTime;
        addScore(s.playerName, s.playerEmail, s.score, s.finishTime);
        s.state = 'winner';
        setGameState('winner');
      }
    }

    s.cameraX = Math.max(0, Math.min(s.player.x - 250, WORLD_WIDTH - WIDTH));
  };

  const draw = () => {
    const ctx = canvasRef.current?.getContext('2d');
    if (!ctx) return;
    
    // Default background
    ctx.fillStyle = '#141e50';
    ctx.fillRect(0, 0, WIDTH, HEIGHT);

    if (s.state === 'name_entry' || s.state === 'highscores') {
      if (imgRef.background && imgRef.background.complete) {
        ctx.drawImage(imgRef.background, 0, 0, WIDTH, HEIGHT);
      }
      return; // React handles overlay UI
    }

    // Background scrolling
    if (imgRef.background && imgRef.background.complete) {
      const bgOffset = Math.floor(s.cameraX * 0.3) % WIDTH;
      ctx.drawImage(imgRef.background, -bgOffset, 0, WIDTH, HEIGHT);
      ctx.drawImage(imgRef.background, WIDTH - bgOffset, 0, WIDTH, HEIGHT);
    }

    // Pipes
    const pipes = [300, 900, 1500, 2100, 2700, 3300, 3900];
    pipes.forEach((px, i) => {
      const ox = px - s.cameraX;
      if (ox > -100 && ox < WIDTH + 100) {
        // pseudo-random height based on position
        const h = 60 + ((px * 13) % 80);
        ctx.fillStyle = PIPE_GREEN; ctx.fillRect(ox, GROUND_Y - h, 52, h);
        ctx.strokeStyle = PIPE_DARK; ctx.lineWidth = 3; ctx.strokeRect(ox, GROUND_Y - h, 52, h);
        ctx.fillStyle = PIPE_GREEN; ctx.fillRect(ox - 5, GROUND_Y - h - 20, 62, 22);
        ctx.strokeRect(ox - 5, GROUND_Y - h - 20, 62, 22);
      }
    });

    // Ground
    if (imgRef.ground && imgRef.ground.complete) {
      const tw = 50;
      const th = 100;
      const startX = -(Math.floor(s.cameraX) % tw);
      for (let tx = startX; tx < WIDTH + tw; tx += tw) {
        ctx.drawImage(imgRef.ground, tx, GROUND_Y, tw, th);
      }
      ctx.fillStyle = DARK_BROWN;
      ctx.fillRect(0, GROUND_Y + th, WIDTH, HEIGHT - GROUND_Y - th);
    } else {
      ctx.fillStyle = '#50c850'; ctx.fillRect(0, GROUND_Y, WIDTH, 20);
      ctx.fillStyle = '#a06432'; ctx.fillRect(0, GROUND_Y + 20, WIDTH, HEIGHT - GROUND_Y);
    }

    // Blocks
    s.blocks.forEach(b => {
      const ox = b.rect.x - s.cameraX;
      if (ox > -100 && ox < WIDTH + 100) {
        if (b.done) {
          ctx.globalAlpha = 0.6;
          if (imgRef.block && imgRef.block.complete) ctx.drawImage(imgRef.block, ox, b.rect.y, 70, 70);
          else { ctx.fillStyle = '#888'; ctx.fillRect(ox, b.rect.y, 70, 70); }
          ctx.globalAlpha = 1;
          ctx.fillStyle = WHITE; ctx.font = '24px Arial'; ctx.fillText("OK", ox + 15, b.rect.y + 42);
        } else {
          ctx.save();
          if (imgRef.block && imgRef.block.complete) {
            ctx.drawImage(imgRef.block, ox, b.rect.y, 70, 70);
            ctx.globalCompositeOperation = 'source-atop';
            const colors = ['rgba(255,255,200,0)','rgba(255,200,100,0.3)','rgba(255,120,50,0.5)','rgba(255,50,50,0.6)',
              'rgba(200,50,255,0.6)','rgba(120,0,255,0.7)','rgba(50,0,200,0.7)','rgba(20,0,150,0.8)',
              'rgba(10,0,100,0.8)','rgba(5,0,20,0.9)'];
            ctx.fillStyle = colors[Math.min(b.level - 1, 9)];
            ctx.fillRect(ox, b.rect.y, 70, 70);
          } else {
            ctx.fillStyle = '#ffb41e'; ctx.fillRect(ox, b.rect.y, 70, 70);
          }
          ctx.restore();
          ctx.fillStyle = b.level >= 6 ? WHITE : BLACK;
          ctx.font = 'bold 36px Arial'; ctx.fillText(b.level.toString(), ox + 25, b.rect.y + 48);
        }
      }
    });

    // Player
    const drawPlayer = (x: number, y: number, alpha = 1) => {
      ctx.globalAlpha = alpha;
      const bob = s.player.vx !== 0 && s.player.onGround ? (Math.floor(s.player.walkFrame / 8) % 2 === 0 ? 3 : -2) : 0;
      
      if (imgRef.trumpRight && imgRef.trumpRight.complete) {
        ctx.save();
        if (s.player.facing === -1) {
          ctx.translate(x + 80, y + bob);
          ctx.scale(-1, 1);
          ctx.drawImage(imgRef.trumpRight, 0, 0, 80, 155);
        } else {
          ctx.drawImage(imgRef.trumpRight, x, y + bob, 80, 155);
        }
        ctx.restore();
      } else {
        ctx.fillStyle = TRUMP_SUIT; ctx.fillRect(x + 6, y + 36 + bob, 68, 80);
        ctx.fillStyle = TRUMP_SKIN; ctx.beginPath(); ctx.arc(x + 40, y + 22 + bob, 22, 0, Math.PI*2); ctx.fill();
      }
      ctx.globalAlpha = 1;
    };

    if (s.state === 'dying') {
      drawPlayer(s.player.x - s.cameraX, s.player.y + s.ghostYOffset, Math.max(0, 1 - s.deathTimer / 100));
    } else {
      drawPlayer(s.player.x - s.cameraX, s.player.y);
    }
  };

  // React UI Rendering
  const now = performance.now() / 1000;
  
  const getQuestionUI = () => {
    if (s.state !== 'question' || !s.currentBlock) return null;
    
    let remaining = 0;
    let label = "";
    if (!s.hasStartedTyping) {
      remaining = Math.max(0, TIME_TO_START - (now - s.questionStartTime));
      label = \`Byrjaðu að skrifa: \${remaining.toFixed(1)}s\`;
    } else {
      remaining = Math.max(0, TIME_TO_FINISH - (now - s.typingStartTime));
      label = \`Tími eftir: \${remaining.toFixed(1)}s\`;
    }
    const ratio = s.hasStartedTyping ? remaining / TIME_TO_FINISH : remaining / TIME_TO_START;
    const barColor = ratio > 0.5 ? GREEN : ratio > 0.25 ? '#ffa500' : RED;

    return (
      <div style={{ position: 'absolute', top: 115, left: 80, right: 80, height: 340, background: '#14143c', border: \`4px solid \${GOLD}\`, borderRadius: '16px', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '20px', color: WHITE, fontFamily: 'sans-serif' }}>
        <h3 style={{ color: GOLD, margin: '0 0 20px 0' }}>— SPURNING {s.score + 1}/10 • STIG {s.currentBlock.level} —</h3>
        <h2 style={{ fontSize: '32px', textAlign: 'center', marginBottom: '30px' }}>{s.currentBlock.question}</h2>
        
        <div style={{ background: '#0a0a28', border: \`2px solid \${GOLD}\`, borderRadius: '10px', width: '80%', padding: '15px 20px', fontSize: '28px', display: 'flex', alignItems: 'center' }}>
          <span style={{ color: GOLD, marginRight: '15px' }}>▶</span>
          <span>{s.inputText}<span style={{ opacity: Date.now() % 1000 > 500 ? 1 : 0 }}>_</span></span>
        </div>
        <p style={{ color: '#9696c8', margin: '20px 0 30px' }}>ENTER = svara  |  BACKSPACE = eyða</p>
        
        <div style={{ width: '90%', marginTop: 'auto' }}>
          <div style={{ color: barColor, marginBottom: '8px', fontWeight: 'bold' }}>{label}</div>
          <div style={{ height: '14px', background: '#1e1e46', borderRadius: '7px', overflow: 'hidden' }}>
            <div style={{ height: '100%', background: barColor, width: \`\${ratio * 100}%\`, transition: 'width 0.1s linear' }} />
          </div>
        </div>
      </div>
    );
  };

  const getHighscoresUI = () => {
    if (gameState !== 'highscores') return null;
    const scores = getScores();
    return (
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,20,0.7)', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '20px', color: WHITE, fontFamily: 'sans-serif' }}>
        <h1 style={{ color: GOLD, fontSize: '48px', margin: '0 0 30px' }}>🏆 HIGH SCORE LISTI 🏆</h1>
        <div style={{ display: 'flex', gap: '40px', width: '90%', maxWidth: '1000px' }}>
          {/* Winners */}
          <div style={{ flex: 1, background: '#14143c', border: \`3px solid \${GOLD}\`, borderRadius: '12px', padding: '20px' }}>
            <h3 style={{ color: GOLD, margin: '0 0 10px' }}>🥇 SIGURVEGARI — BESTUR TÍMI</h3>
            <hr style={{ borderColor: GOLD, marginBottom: '20px' }}/>
            {scores.winners.length > 0 ? scores.winners.map((w: any, i: number) => {
              const m = Math.floor(w.time / 60);
              const sec = (w.time % 60).toFixed(2);
              const color = i===0?GOLD:i===1?'#c0c0c0':i===2?'#cd7f32':WHITE;
              const medal = i===0?'🥇':i===1?'🥈':i===2?'🥉':\`#\${i+1}\`;
              return (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', color, marginBottom: '15px', fontSize: '20px' }}>
                  <div>
                    <div style={{ fontWeight: 'bold' }}>{medal} {w.name}</div>
                    <div style={{ fontSize: '14px', color: '#78a0c8' }}>{w.email}</div>
                  </div>
                  <div>{m > 0 ? \`\${m}:\${sec.padStart(5,'0')}\` : \`\${sec}s\`}</div>
                </div>
              );
            }) : <div style={{ color: '#9696c8' }}>Enginn hefur unnið ennþá!</div>}
          </div>
          {/* Best Scores */}
          <div style={{ flex: 1, background: '#14143c', border: '3px solid #9664c8', borderRadius: '12px', padding: '20px' }}>
            <h3 style={{ color: '#c896ff', margin: '0 0 10px' }}>📊 FLESTAR RÉTTAR SPURNINGAR</h3>
            <hr style={{ borderColor: '#9664c8', marginBottom: '20px' }}/>
            {scores.best_scores.length > 0 ? scores.best_scores.map((s: any, i: number) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', color: i===0?GOLD:WHITE, marginBottom: '15px', fontSize: '20px' }}>
                <div>
                  <div style={{ fontWeight: 'bold' }}>#{i+1} {s.name}</div>
                  <div style={{ fontSize: '14px', color: '#78a0c8' }}>{s.email}</div>
                </div>
                <div>{s.score}/10</div>
              </div>
            )) : <div style={{ color: '#9696c8' }}>Enginn hefur spilað ennþá!</div>}
          </div>
        </div>
        <div style={{ marginTop: '30px', fontSize: '24px', color: '#96c8ff' }}>► SPACE = Til baka ◄</div>
      </div>
    );
  };

  const getNameEntryUI = () => {
    if (gameState !== 'name_entry') return null;
    return (
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,20,0.6)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: WHITE, fontFamily: 'sans-serif' }}>
        <h1 style={{ color: GOLD, fontSize: '64px', margin: '0 0 10px', textShadow: '2px 2px 0 #000' }}>QUIZ WALKER</h1>
        <p style={{ color: '#ff9696', fontSize: '24px', margin: '0 0 40px' }}>Trump er að bíða eftir þér... 😈</p>
        
        <div style={{ width: '600px', background: '#14143c', border: \`3px solid \${s.nameFieldActive ? GOLD : '#505078'}\`, borderRadius: '10px', padding: '15px 20px', marginBottom: '20px', display: 'flex', alignItems: 'center' }}>
          <span style={{ color: '#b4b4ff', fontSize: '24px', width: '120px' }}>👤 Nafn:</span>
          <span style={{ fontSize: '28px', fontWeight: 'bold' }}>{s.playerName}<span style={{ opacity: s.nameFieldActive && Date.now() % 1000 > 500 ? 1 : 0 }}>_</span></span>
        </div>

        <div style={{ width: '600px', background: '#14143c', border: \`3px solid \${!s.nameFieldActive ? GOLD : '#505078'}\`, borderRadius: '10px', padding: '15px 20px', marginBottom: '30px', display: 'flex', alignItems: 'center' }}>
          <span style={{ color: '#b4b4ff', fontSize: '24px', width: '120px' }}>✉ Email:</span>
          <span style={{ fontSize: '28px', fontWeight: 'bold' }}>{s.playerEmail}<span style={{ opacity: !s.nameFieldActive && Date.now() % 1000 > 500 ? 1 : 0 }}>_</span></span>
        </div>

        <div style={{ color: '#7878a0', marginBottom: '30px' }}>TAB = skipta á milli reita</div>

        {s.playerName.trim() && s.playerEmail.trim() ? (
          <div style={{ color: GREEN, fontSize: '28px', fontWeight: 'bold', animation: 'pulse 1s infinite' }}>► ENTER TIL AÐ BYRJA ◄</div>
        ) : (
          <div style={{ color: '#7878a0', fontSize: '24px' }}>Skrifaðu {s.playerName.trim() ? "email..." : "nafnið þitt..."}</div>
        )}
        
        <div style={{ color: '#9696c8', marginTop: '40px' }}>H = High Score listi</div>
      </div>
    );
  };

  return (
    <div style={{ width: '100vw', height: '100vh', background: '#050a11', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ position: 'relative', width: WIDTH, height: HEIGHT, borderRadius: '14px', overflow: 'hidden', boxShadow: '0 20px 50px rgba(0,0,0,0.8)' }}>
        <canvas ref={canvasRef} width={WIDTH} height={HEIGHT} style={{ display: 'block' }} />
        
        {/* HUD Overlay for playing mode */}
        {(gameState === 'playing' || gameState === 'question' || gameState === 'dying' || gameState === 'winner') && (
          <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 90, background: 'rgba(40,40,40,0.9)', borderBottom: \`3px solid \${GOLD}\`, color: WHITE, fontFamily: 'sans-serif', padding: '15px 30px', pointerEvents: 'none' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '24px', fontWeight: 'bold' }}>
              <span>SPURNING: {s.score + 1}/{TOTAL_QUESTIONS}</span>
              <span style={{ color: GOLD }}>RÉTT: {s.score}</span>
              <span style={{ color: '#b4b4ff' }}>STIG: {Math.min(s.score + 1, MAX_LEVEL)}</span>
              <span>⏱ {s.gameStartTime ? (now - s.gameStartTime).toFixed(1) + 's' : '0.0s'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', fontSize: '18px' }}>
              <span style={{ color: '#b4dcff' }}>👤 {s.playerName}</span>
              <span style={{ color: s.message.includes('Rétt') ? GOLD : '#ccc' }}>{s.message}</span>
            </div>
          </div>
        )}

        {getQuestionUI()}

        {/* Dying Screen */}
        {gameState === 'dying' && s.deathTimer >= 80 && (
          <div style={{ position: 'absolute', inset: 0, background: \`rgba(0,0,0,\${s.fadeAlpha})\`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: WHITE, fontFamily: 'sans-serif' }}>
            {s.deathAnimationDone && (
              <>
                {imgRef.trumpRage && <img src="/trumprage.png" alt="Rage" style={{ width: 250, marginBottom: 20 }} />}
                <h1 style={{ color: RED, fontSize: '48px', margin: '0 0 10px 0', textShadow: '2px 2px 0 #000' }}>{s.rageLine1}</h1>
                <h2 style={{ fontSize: '28px', fontWeight: 'normal', margin: '0 0 30px 0' }}>{s.rageLine2}</h2>
                <p style={{ color: GOLD, fontSize: '24px', animation: 'pulse 1s infinite' }}>► ÝTTU Á SPACE TIL AÐ REYNA AFTUR ◄</p>
              </>
            )}
          </div>
        )}

        {/* Winner Screen */}
        {gameState === 'winner' && (
          <div style={{ position: 'absolute', top: 100, left: 100, right: 100, bottom: 120, background: '#14143c', border: \`5px solid \${GOLD}\`, borderRadius: '18px', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '40px', color: WHITE, fontFamily: 'sans-serif' }}>
            <h1 style={{ color: GOLD, fontSize: '54px', margin: '0 0 20px 0' }}>🏆 SIGURVEGARI! 🏆</h1>
            <h2 style={{ fontSize: '28px', margin: '0 0 20px 0' }}>{s.playerName} — ÓTRÚLEGT!</h2>
            <h3 style={{ color: GOLD, fontSize: '32px', margin: '0 0 20px 0' }}>Tíminn þinn: {s.finishTime.toFixed(2)} sekúndur</h3>
            <h3 style={{ color: RED, fontSize: '24px', margin: '0 0 20px 0' }}>Hafðu samband við skipuleggjanda!</h3>
            <p style={{ color: '#b4b4b4', marginBottom: '30px' }}>Even Trump is impressed... maybe.</p>
            <p style={{ color: '#96c8ff' }}>SPACE = Sjá high score  |  R = Reyna aftur</p>
          </div>
        )}

        {getNameEntryUI()}
        {getHighscoresUI()}

        <style>{`
          @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
          }
        `}</style>
      </div>
    </div>
  );
}
