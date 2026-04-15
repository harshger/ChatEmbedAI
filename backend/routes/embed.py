from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(tags=["embed"])

EMBED_JS_TEMPLATE = """
(function() {
  var script = document.currentScript;
  var chatbotId = script.getAttribute('data-chatbot-id');
  var lang = script.getAttribute('data-lang') || 'de';
  var apiBase = script.src.replace('/api/embed.js', '');

  var translations = {
    de: { gdpr: 'Dieser Chat wird von ChatEmbed AI bereitgestellt. Nachrichten werden zur Verarbeitung an KI-Server übertragen.', consent: 'Verstanden & fortfahren', privacy: 'Datenschutz', placeholder: 'Nachricht eingeben...', powered: 'Powered by ChatEmbed AI', badge: 'KI-Chat', blocked: 'Dieses Chat-Widget ist für diese Domain nicht autorisiert.' },
    en: { gdpr: 'This chat is provided by ChatEmbed AI. Messages are transmitted to AI servers for processing.', consent: 'Understood & Continue', privacy: 'Privacy Policy', placeholder: 'Type a message...', powered: 'Powered by ChatEmbed AI', badge: 'AI Chat', blocked: 'This chat widget is not authorized for this domain.' }
  };
  var t = translations[lang] || translations.de;

  var style = document.createElement('style');
  style.textContent = `
    #ce-widget-btn { position:fixed; bottom:24px; right:24px; width:56px; height:56px; border-radius:50%; border:none; cursor:pointer; z-index:99998; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 20px rgba(0,0,0,0.2); transition:transform 0.2s; }
    #ce-widget-btn:hover { transform:scale(1.08); }
    #ce-widget-btn svg { fill:white; width:24px; height:24px; }
    #ce-widget-window { position:fixed; bottom:90px; right:24px; width:360px; height:520px; background:#fff; border:1px solid #e5e7eb; box-shadow:0 8px 32px rgba(0,0,0,0.12); z-index:99999; display:none; flex-direction:column; overflow:hidden; font-family:'IBM Plex Sans',-apple-system,sans-serif; }
    #ce-widget-window.ce-open { display:flex; animation:ce-slide-up 0.25s ease-out; }
    @keyframes ce-slide-up { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
    #ce-widget-header { padding:12px 16px; color:white; display:flex; align-items:center; justify-content:space-between; }
    #ce-widget-header h4 { margin:0; font-size:14px; font-weight:700; }
    #ce-widget-header span { font-size:11px; opacity:0.75; }
    #ce-widget-close { background:none; border:none; color:white; cursor:pointer; font-size:18px; padding:4px; }
    #ce-widget-gdpr { padding:20px; background:#f9fafb; border-bottom:1px solid #e5e7eb; flex:1; display:flex; flex-direction:column; justify-content:center; }
    #ce-widget-gdpr p { font-size:12px; color:#0a0a0a; line-height:1.6; margin:0 0 16px; }
    #ce-widget-gdpr button { color:white; border:none; padding:8px 16px; font-size:12px; font-weight:700; cursor:pointer; }
    #ce-widget-gdpr a { color:#002FA7; text-decoration:underline; }
    #ce-widget-messages { flex:1; overflow-y:auto; padding:16px; }
    .ce-msg { max-width:80%; padding:8px 12px; margin-bottom:8px; font-size:13px; line-height:1.5; word-wrap:break-word; }
    .ce-msg-user { margin-left:auto; color:white; }
    .ce-msg-bot { background:#f3f4f6; color:#0a0a0a; }
    .ce-typing { display:flex; gap:4px; padding:8px 12px; background:#f3f4f6; width:fit-content; }
    .ce-typing span { width:6px; height:6px; background:#9ca3af; border-radius:50%; animation:ce-bounce 1.2s infinite; }
    .ce-typing span:nth-child(2) { animation-delay:0.2s; }
    .ce-typing span:nth-child(3) { animation-delay:0.4s; }
    @keyframes ce-bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-4px)} }
    #ce-widget-input { padding:12px; border-top:1px solid #e5e7eb; display:flex; gap:8px; }
    #ce-widget-input input { flex:1; border:1px solid #e5e7eb; padding:8px 12px; font-size:13px; outline:none; }
    #ce-widget-input input:focus { border-color:#002FA7; }
    #ce-widget-input button { border:none; color:white; padding:8px 12px; cursor:pointer; font-size:13px; }
    #ce-widget-footer { padding:6px 12px; border-top:1px solid #f3f4f6; display:flex; justify-content:space-between; font-size:10px; color:#9ca3af; }
    #ce-widget-footer a { color:#002FA7; text-decoration:none; }
    @media(max-width:480px) { #ce-widget-window { bottom:0; right:0; left:0; width:100%; height:100%; } }
  `;
  document.head.appendChild(style);

  var state = { open:false, consented:false, messages:[], typing:false, sessionId:'ce_'+Date.now()+'_'+Math.random().toString(36).substr(2,6) };
  var color = '#6366f1';
  var businessName = '';
  var showGdpr = true;

  // Fetch chatbot config with domain lock check
  fetch(apiBase+'/api/chatbot-public/'+chatbotId).then(function(r){return r.json()}).then(function(d){
    // Domain lock: block widget if domain is verified and current host doesn't match
    var allowedDomain = d.allowed_domain || '';
    var domainVerified = d.domain_verified || false;
    var currentHost = window.location.hostname.replace(/^www\\./, '');
    var normalizedAllowed = allowedDomain.replace(/^www\\./, '');

    if (domainVerified && normalizedAllowed && currentHost !== normalizedAllowed) {
      btn.style.display = 'none';
      console.warn('[ChatEmbed] Widget blocked: domain mismatch. Allowed: ' + normalizedAllowed + ', Current: ' + currentHost);
      return;
    }

    color = d.widget_color || '#6366f1';
    businessName = d.business_name || '';
    showGdpr = d.show_gdpr_notice !== false;
    btn.style.background = color;
    header.style.background = color;
    sendBtn.style.background = color;
    consentBtn.style.background = color;
    headerTitle.textContent = businessName;
    if(!showGdpr) { state.consented=true; gdprDiv.style.display='none'; msgDiv.style.display='block'; inputDiv.style.display='flex'; footerDiv.style.display='flex'; }
  });

  // Build DOM
  var btn = document.createElement('button');
  btn.id='ce-widget-btn';
  btn.innerHTML='<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>';
  btn.style.background=color;
  btn.onclick=function(){ state.open=!state.open; win.classList.toggle('ce-open',state.open); btn.style.display=state.open?'none':'flex'; };
  document.body.appendChild(btn);

  var win = document.createElement('div');
  win.id='ce-widget-window';
  
  var header = document.createElement('div');
  header.id='ce-widget-header';
  header.style.background=color;
  var headerTitle = document.createElement('h4');
  headerTitle.textContent=businessName;
  var headerBadge = document.createElement('span');
  headerBadge.textContent=t.badge;
  var headerLeft = document.createElement('div');
  headerLeft.appendChild(headerTitle);
  headerLeft.appendChild(headerBadge);
  var closeBtn = document.createElement('button');
  closeBtn.id='ce-widget-close';
  closeBtn.innerHTML='&times;';
  closeBtn.onclick=function(){ state.open=false; win.classList.remove('ce-open'); btn.style.display='flex'; };
  header.appendChild(headerLeft);
  header.appendChild(closeBtn);
  win.appendChild(header);

  var gdprDiv = document.createElement('div');
  gdprDiv.id='ce-widget-gdpr';
  var gdprText = document.createElement('p');
  gdprText.innerHTML=t.gdpr+' <a href="/datenschutz" target="_blank">'+t.privacy+'</a>';
  var consentBtn = document.createElement('button');
  consentBtn.textContent=t.consent;
  consentBtn.style.background=color;
  consentBtn.onclick=function(){ state.consented=true; gdprDiv.style.display='none'; msgDiv.style.display='block'; inputDiv.style.display='flex'; footerDiv.style.display='flex'; };
  gdprDiv.appendChild(gdprText);
  gdprDiv.appendChild(consentBtn);
  win.appendChild(gdprDiv);

  var msgDiv = document.createElement('div');
  msgDiv.id='ce-widget-messages';
  msgDiv.style.display='none';
  win.appendChild(msgDiv);

  var inputDiv = document.createElement('div');
  inputDiv.id='ce-widget-input';
  inputDiv.style.display='none';
  var inputField = document.createElement('input');
  inputField.placeholder=t.placeholder;
  inputField.onkeydown=function(e){ if(e.key==='Enter') sendMessage(); };
  var sendBtn = document.createElement('button');
  sendBtn.textContent='>';
  sendBtn.style.background=color;
  sendBtn.onclick=sendMessage;
  inputDiv.appendChild(inputField);
  inputDiv.appendChild(sendBtn);
  win.appendChild(inputDiv);

  var footerDiv = document.createElement('div');
  footerDiv.id='ce-widget-footer';
  footerDiv.style.display='none';
  footerDiv.innerHTML='<span>'+t.powered+'</span><a href="/datenschutz" target="_blank">'+t.privacy+'</a>';
  win.appendChild(footerDiv);
  document.body.appendChild(win);

  function addMessage(role, text) {
    var div = document.createElement('div');
    div.className='ce-msg ce-msg-'+(role==='user'?'user':'bot');
    if(role==='user') div.style.background=color;
    div.textContent=text;
    msgDiv.appendChild(div);
    msgDiv.scrollTop=msgDiv.scrollHeight;
  }

  function sendMessage() {
    var text=inputField.value.trim();
    if(!text) return;
    inputField.value='';
    addMessage('user',text);
    state.messages.push({role:'user',content:text});
    var typingDiv=document.createElement('div');
    typingDiv.className='ce-typing';
    typingDiv.innerHTML='<span></span><span></span><span></span>';
    msgDiv.appendChild(typingDiv);
    msgDiv.scrollTop=msgDiv.scrollHeight;
    fetch(apiBase+'/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({chatbot_id:chatbotId,message:text,session_id:state.sessionId,history:state.messages.slice(0,-1),widget_consent:true})}).then(function(r){return r.json()}).then(function(d){
      typingDiv.remove();
      var resp=d.response||'Error';
      addMessage('assistant',resp);
      state.messages.push({role:'assistant',content:resp});
    }).catch(function(){
      typingDiv.remove();
      addMessage('assistant','Entschuldigung, ein Fehler ist aufgetreten.');
    });
  }
})();
"""


@router.get("/embed.js")
async def serve_embed_js():
    return PlainTextResponse(EMBED_JS_TEMPLATE, media_type="application/javascript")
