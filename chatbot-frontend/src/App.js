import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [token, setToken] = useState(null);
  const [currentView, setCurrentView] = useState('chat'); 
  
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [genre, setGenre] = useState("Ação");
  const [age, setAge] = useState("");
  const [platforms, setPlatforms] = useState([]);
  const [showPassword, setShowPassword] = useState(false);
  
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isRegistering, setIsRegistering] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  
  const [movieSearchQuery, setMovieSearchQuery] = useState("");
  const [movieSearchResults, setMovieSearchResults] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [newReviewRating, setNewReviewRating] = useState(5);
  const [newReviewComment, setNewReviewComment] = useState("");

  // Estado para vídeo (Modal)
  const [videoUrl, setVideoUrl] = useState(null);

  const fileInputRef = useRef(null);
  const [uploadType, setUploadType] = useState(null);
  const [editingImage, setEditingImage] = useState(null);
  const [imagePos, setImagePos] = useState({ x: 50, y: 50 });
  const [isEditingBio, setIsEditingBio] = useState(false);
  const [tempBio, setTempBio] = useState("");

  const messagesEndRef = useRef(null);
  const availablePlatforms = ["Netflix", "Prime Video", "Disney+", "HBO Max", "Globoplay"];

  useEffect(() => {
    sessionStorage.removeItem('token');
    localStorage.removeItem('token');
    setToken(null);
  }, []);

  useEffect(() => {
    if (currentView === 'chat') messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentView]);

  useEffect(() => {
    setStatusMsg(null);
    setUsername("");
    setPassword("");
    setEmail("");
  }, [isRegistering, isResetting]);

  useEffect(() => {
    if (token && currentView === 'profile') fetchProfile();
  }, [token, currentView]);

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (movieSearchQuery.length > 2) searchMovies(movieSearchQuery);
      else setMovieSearchResults([]);
    }, 500);
    return () => clearTimeout(delayDebounceFn);
  }, [movieSearchQuery]);

  const fetchProfile = async () => {
    try {
      const res = await fetch('http://127.0.0.1:5000/profile', { headers: { 'Authorization': `Bearer ${token}` } });
      const data = await res.json();
      if (res.ok) { setUserProfile(data); setTempBio(data.bio); }
    } catch (err) { console.error(err); }
  };

  const searchMovies = async (query) => {
    try {
      const res = await fetch(`http://127.0.0.1:5000/movies/search?query=${query}`, { headers: { 'Authorization': `Bearer ${token}` } });
      const data = await res.json();
      if (res.ok) setMovieSearchResults(data);
    } catch (err) { console.error(err); }
  };

  const togglePlatform = (p) => {
    setPlatforms(prev => prev.includes(p) ? prev.filter(x => x !== p) : [...prev, p]);
  };

  const RobotIcon = () => (<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="2" y="6" width="20" height="14" rx="4"/><path d="M6 6V3H18V6"/><circle cx="12" cy="3" r="1.5"/><path d="M8 11H10"/><path d="M14 11H16"/><path d="M9 15C9 15 10 16 12 16C14 16 15 15 15 15"/></svg>);
  const EditIcon = () => (<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>);
  const SearchIcon = () => (<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>);
  const TrashIcon = () => (<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>);
  const UploadIcon = () => (<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>);
  const ArrowsH = () => (<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12H3m18 0-4-4m4 4-4 4M3 12l4-4m-4 4 4 4"/></svg>);
  const ArrowsV = () => (<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 3v18m0-18-4 4m4-4 4 4M12 21l-4-4m4 4 4-4"/></svg>);
  const PlayIcon = () => (<svg width="16" height="16" viewBox="0 0 24 24" fill="white" stroke="currentColor" strokeWidth="0"><path d="M8 5v14l11-7z"/></svg>);
  const PlusIcon = () => (<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>);

  const ClaqueteFechada = () => (<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="3" y="11" width="18" height="10" rx="2" fill="#1e293b" stroke="#64748b" strokeWidth="1.5"/><path d="M3 9C3 7.89543 3.89543 7 5 7H19C20.1046 7 21 7.89543 21 9V11H3V9Z" fill="#3b82f6" stroke="#64748b" strokeWidth="1.5"/><path d="M7 7L5 11M11 7L9 11M15 7L13 11M19 7L17 11" stroke="#0f172a" strokeWidth="1.5" strokeLinecap="round"/></svg>);
  const ClaqueteAberta = () => (<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="3" y="11" width="18" height="10" rx="2" fill="#1e293b" stroke="#64748b" strokeWidth="1.5"/><g transform="rotate(-20 3 11)"><path d="M3 7C3 5.89543 3.89543 5 5 5H19C20.1046 5 21 5.89543 21 7V9H3V7Z" fill="#60a5fa" stroke="#64748b" strokeWidth="1.5"/><path d="M7 5L5 9M11 5L9 9M15 5L13 9M19 5L17 9" stroke="#0f172a" strokeWidth="1.5" strokeLinecap="round"/></g></svg>);

  const handleAuth = async (e) => {
    e.preventDefault();
    setStatusMsg({ type: 'loading', text: 'Processando...' });
    const endpoint = isRegistering ? '/register' : (isResetting ? '/reset-password' : '/login');
    const payload = isRegistering 
      ? { username, password, email, genre, age, streaming: platforms.join(', ') }
      : (isResetting ? { username, email, new_password: password } : { username, password });

    try {
      const res = await fetch(`http://127.0.0.1:5000${endpoint}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (res.ok) {
        if (isRegistering || isResetting) {
          setStatusMsg({ type: 'success', text: 'Sucesso! Faça login.' });
          setIsRegistering(false); setIsResetting(false);
        } else {
          setToken(data.access_token); sessionStorage.setItem('token', data.access_token);
          setMessages([{ role: 'model', text: `Olá, ${username}! O que vamos assistir hoje?` }]);
          setStatusMsg(null); setCurrentView('chat');
        }
      } else {
        setStatusMsg({ type: 'error', text: data.msg || "Erro" });
      }
    } catch (error) { setStatusMsg({ type: 'error', text: "Erro de conexão." }); }
  };

  const handleLogout = () => {
    setToken(null); sessionStorage.removeItem('token'); localStorage.removeItem('token');
    setMessages([]); setStatusMsg(null); setUserProfile(null); setCurrentView('chat');
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput(""); setLoading(true);

    try {
      const res = await fetch('http://127.0.0.1:5000/chat', {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ mensagem: userMsg.text })
      });
      const data = await res.json();
      if (res.ok) {
        setMessages(prev => [...prev, { 
          role: 'model', 
          text: data.text || data.resposta, 
          movies: data.movies 
        }]);
      } else if (res.status === 401) handleLogout();
    } catch (error) {
      setMessages(prev => [...prev, { role: 'model', text: "Erro de conexão." }]);
    }
    setLoading(false);
  };

  const requestSimilarMovies = async (movieId, title) => {
    setLoading(true);
    const userMsg = { role: 'user', text: `Filmes parecidos com ${title}` };
    setMessages(prev => [...prev, userMsg]);
    try {
       const res = await fetch(`http://127.0.0.1:5000/movies/similar/${movieId}`, { headers: { 'Authorization': `Bearer ${token}` } });
       const data = await res.json();
       if (res.ok && data.length > 0) {
           setMessages(prev => [...prev, { role: 'model', text: `Aqui estão sugestões similares a ${title}:`, movies: data }]);
       } else {
           setMessages(prev => [...prev, { role: 'model', text: "Não encontrei similares no momento." }]);
       }
    } catch(err) {}
    setLoading(false);
  };

  const playTrailer = async (movieId) => {
      try {
          const res = await fetch(`http://127.0.0.1:5000/movies/video/${movieId}`, { headers: { 'Authorization': `Bearer ${token}` } });
          const data = await res.json();
          if (res.ok && data.key) setVideoUrl(`https://www.youtube.com/embed/${data.key}?autoplay=1`);
          else alert("Trailer não disponível.");
      } catch(err) {}
  };

  const submitReview = async () => {
      if (!selectedMovie) return;
      try {
        const res = await fetch('http://127.0.0.1:5000/reviews', {
          method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ title: selectedMovie.title, rating: newReviewRating, poster_url: selectedMovie.poster, comment: newReviewComment })
        });
        if (res.ok) { setSelectedMovie(null); setMovieSearchQuery(""); setMovieSearchResults([]); setNewReviewComment(""); fetchProfile(); }
      } catch (err) {}
  };

  const deleteReview = async (id) => {
    if(!window.confirm("Apagar filme?")) return;
    try {
        const res = await fetch(`http://127.0.0.1:5000/reviews/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
        if(res.ok) fetchProfile();
    } catch(err){}
  };

  const startImageEdit = (type) => {
      setUploadType(type);
      const initX = type === 'avatar_url' ? userProfile.avatar_pos_x : userProfile.banner_pos_x;
      const initY = type === 'avatar_url' ? userProfile.avatar_pos_y : userProfile.banner_pos_y;
      setImagePos({ x: initX || 50, y: initY || 50 });
      setEditingImage(type === 'avatar_url' ? 'avatar' : 'banner');
  };

  const cancelImageEdit = () => {
    setEditingImage(null);
    setUploadType(null);
  };

  const saveImagePos = async () => {
      const fieldX = editingImage === 'avatar' ? 'avatar_pos_x' : 'banner_pos_x';
      const fieldY = editingImage === 'avatar' ? 'avatar_pos_y' : 'banner_pos_y';
      try {
        const res = await fetch('http://127.0.0.1:5000/profile/update', {
          method: 'PUT', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ [fieldX]: imagePos.x, [fieldY]: imagePos.y })
        });
        if (res.ok) { fetchProfile(); setEditingImage(null); }
      } catch (err) {}
  };

  const handleFileChange = (e) => {
      const file = e.target.files[0];
      if(!file) return;
      const reader = new FileReader();
      reader.onloadend = async () => {
          try {
             const res = await fetch('http://127.0.0.1:5000/profile/update', {
                 method: 'PUT', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                 body: JSON.stringify({ [uploadType]: reader.result })
             });
             if(res.ok) fetchProfile();
          } catch(err){}
      };
      reader.readAsDataURL(file);
  };
  
  const handleUpdateBio = async () => {
      try {
          const res = await fetch('http://127.0.0.1:5000/profile/update', {
             method: 'PUT', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
             body: JSON.stringify({ bio: tempBio })
          });
          if(res.ok) { fetchProfile(); setIsEditingBio(false); }
      } catch(err){}
  };

  if (!token) {
    return (
      <div className="app-container auth-container">
        <div className="auth-box">
          <div style={{display:'flex', alignItems:'center', justifyContent:'center', gap:'10px', marginBottom:'10px'}}>
            <RobotIcon />
            <h1 style={{margin:0, fontSize:'2rem', fontWeight:'800'}}>CineBot</h1>
          </div>
          <h3 style={{textAlign:'center', color:'#60a5fa', margin:'0 0 20px 0'}}>{isRegistering ? 'Cadastro' : isResetting ? 'Recuperar' : 'Login'}</h3>
          
          <form onSubmit={handleAuth}>
            <div className="input-group"><input className="input-field" placeholder="Usuário" value={username} required onChange={e => setUsername(e.target.value)} /></div>
            {(isRegistering || isResetting) && (<div className="input-group"><input className="input-field" type="email" placeholder="Email" value={email} required onChange={e => setEmail(e.target.value)} /></div>)}
            <div className="input-group">
                <input className="input-field" type={showPassword ? "text" : "password"} placeholder="Senha" value={password} required onChange={e => setPassword(e.target.value)} />
                <button type="button" onClick={() => setShowPassword(!showPassword)} style={{position:'absolute', right:'12px', top:'50%', transform:'translateY(-50%)', background:'none', border:'none', cursor:'pointer', color:'#94a3b8'}}>{showPassword ? <ClaqueteAberta /> : <ClaqueteFechada />}</button>
            </div>
            {isRegistering && (
                <>
                <div className="input-group" style={{display:'flex', gap:'10px'}}>
                    <select className="input-field" value={genre} onChange={e => setGenre(e.target.value)}><option>Ação</option><option>Comédia</option><option>Drama</option><option>Ficção</option><option>Terror</option></select>
                    <input className="input-field" type="text" inputMode="numeric" placeholder="Idade" value={age} required onChange={e => setAge(e.target.value.replace(/\D/g, '').substring(0,2))} style={{width:'80px'}} />
                </div>
                <div className="checkbox-group">{availablePlatforms.map(p => (<div key={p} className={`checkbox-pill ${platforms.includes(p) ? 'active' : ''}`} onClick={() => togglePlatform(p)}>{platforms.includes(p) ? '✓' : '+'} {p}</div>))}</div>
                </>
            )}
            {statusMsg && <div className={`status-msg ${statusMsg.type === 'error' ? 'status-error' : 'status-success'}`}>{statusMsg.text}</div>}
            <button type="submit" className="primary-btn">{isRegistering ? 'Cadastrar' : isResetting ? 'Redefinir' : 'Entrar'}</button>
          </form>
          {!isResetting && !isRegistering && <div className="link-text" style={{marginTop:'20px', fontSize:'0.8rem'}} onClick={() => setIsResetting(true)}>Esqueci minha senha</div>}
          <div className="link-text" onClick={() => {setIsRegistering(!isRegistering); setIsResetting(false)}}>{isRegistering || isResetting ? 'Voltar para Login' : 'Criar conta'}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <input type="file" ref={fileInputRef} style={{display:'none'}} accept="image/*" onChange={handleFileChange} />
      
      {videoUrl && (
        <div className="video-modal" onClick={() => setVideoUrl(null)}>
          <div className="video-container">
            <iframe src={videoUrl} title="Trailer" frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen></iframe>
          </div>
        </div>
      )}

      <div className="header">
        <div className="brand"><RobotIcon /> CineBot</div>
        <div className="desktop-nav">
          <div className={`desktop-link ${currentView === 'chat' ? 'active' : ''}`} onClick={() => setCurrentView('chat')}>Chat</div>
          <div className={`desktop-link ${currentView === 'profile' ? 'active' : ''}`} onClick={() => setCurrentView('profile')}>Perfil</div>
        </div>
        <button className="logout-btn" onClick={handleLogout}>Sair</button>
      </div>

      <div className="content-area">
        {currentView === 'chat' ? (
          <>
            <div className="messages-list">
              {messages.map((msg, i) => (
                <div key={i} style={{width: '100%', display: 'flex', flexDirection: 'column', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start'}}>
                  {msg.text && (
                    <div className={`msg-bubble ${msg.role === 'user' ? 'msg-user' : 'msg-bot'}`}>
                      {msg.text}
                    </div>
                  )}
                  {msg.movies && (
                    <div className="chat-movies-grid">
                      {msg.movies.map((movie, idx) => (
                        <div key={idx} className="chat-movie-card">
                          <div className="poster-wrapper">
                            <img src={movie.poster} alt={movie.title} className="chat-movie-poster" onError={(e) => e.target.src = 'https://via.placeholder.com/150x225?text=Sem+Poster'} />
                            {movie.id && (
                              <div className="movie-overlay">
                                <button className="action-btn" onClick={() => playTrailer(movie.id)} title="Ver Trailer"><PlayIcon/></button>
                                <button className="action-btn" onClick={() => requestSimilarMovies(movie.id, movie.title)} title="Ver Similares"><PlusIcon/></button>
                              </div>
                            )}
                          </div>
                          <div className="chat-movie-info">
                            <div className="chat-movie-title">{movie.title}</div>
                            <div className="chat-movie-year">{movie.year}</div>
                            <div className="chat-movie-desc">{movie.reason}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              {loading && <div style={{color:'#94a3b8', padding:'0 20px'}}>Digitando...</div>}
              <div ref={messagesEndRef} />
            </div>
            <div className="input-area">
              <input className="chat-input" placeholder="Digite aqui..." value={input} onChange={e => setInput(e.target.value)} onKeyPress={e => e.key === 'Enter' && sendMessage()} />
              <button className="send-btn" onClick={sendMessage}>➤</button>
            </div>
          </>
        ) : (
          <div className="profile-view">
             {userProfile && (
              <>
                <div className="banner" style={{backgroundImage: `url(${userProfile.banner_url})`, backgroundPosition: `${userProfile.banner_pos_x}% ${userProfile.banner_pos_y}%`}}>
                  <button className="edit-btn" onClick={() => startImageEdit('banner_url')}><EditIcon/></button>
                </div>
                
                {editingImage && (
                  <div className="image-adjust-panel">
                    <div className="upload-dropzone" onClick={() => fileInputRef.current.click()}><UploadIcon/><span>Carregar Nova</span></div>
                    <div className="slider-container"><div className="slider-icon"><ArrowsH/></div><input type="range" value={imagePos.x} onChange={e => {setImagePos({...imagePos, x: e.target.value}); document.querySelector(`.${editingImage}`).style.backgroundPosition = `${e.target.value}% ${imagePos.y}%`}} className="range-slider"/></div>
                    <div className="slider-container"><div className="slider-icon"><ArrowsV/></div><input type="range" value={imagePos.y} onChange={e => {setImagePos({...imagePos, y: e.target.value}); document.querySelector(`.${editingImage}`).style.backgroundPosition = `${imagePos.x}% ${e.target.value}%`}} className="range-slider"/></div>
                    <div className="panel-actions"><button className="panel-btn cancel-pos-btn" onClick={cancelImageEdit}>X</button><button className="panel-btn save-pos-btn" onClick={saveImagePos}>Salvar</button></div>
                  </div>
                )}

                <div className="profile-header">
                  <div className="avatar" style={{backgroundImage: `url(${userProfile.avatar_url})`, backgroundPosition: `${userProfile.avatar_pos_x}% ${userProfile.avatar_pos_y}%`}}>
                    <button className="edit-btn" onClick={() => startImageEdit('avatar_url')}><EditIcon/></button>
                  </div>
                  <div className="user-info">
                    <h2 className="user-name">{userProfile.username}</h2>
                    {isEditingBio ? (
                        <div><textarea value={tempBio} onChange={e=>setTempBio(e.target.value)} className="comment-area"/><button onClick={handleUpdateBio} className="primary-btn" style={{padding:'5px', fontSize:'0.8rem', marginTop:'5px'}}>Salvar</button></div>
                    ) : (
                        <div onClick={()=>setIsEditingBio(true)} style={{cursor:'pointer'}}><p className="user-bio">{userProfile.bio} ✎</p></div>
                    )}
                  </div>
                </div>

                <div style={{display:'grid', gridTemplateColumns: window.innerWidth > 768 ? '1fr 1fr' : '1fr', gap:'30px'}}>
                    <div>
                        <h3 className="section-title">Avaliar Filme</h3>
                        <div className="review-form">
                            {!selectedMovie ? (
                                <div style={{position:'relative'}}>
                                    <div className="search-container"><div className="search-icon-pos"><SearchIcon/></div><input className="search-input-modern" placeholder="Pesquisar..." value={movieSearchQuery} onChange={e=>setMovieSearchQuery(e.target.value)}/></div>
                                    {movieSearchResults.length > 0 && <div className="search-results-list">{movieSearchResults.map(m => (<div key={m.id} className="search-result-item" onClick={()=>{setSelectedMovie(m); setMovieSearchResults([])}}><img src={m.poster} className="search-result-poster"/><div><strong>{m.title}</strong><br/><small>{m.year}</small></div></div>))}</div>}
                                </div>
                            ) : (
                                <div className="selected-movie-preview">
                                    <img src={selectedMovie.poster} className="selected-poster"/>
                                    <div style={{flex:1}}>
                                        <h3>{selectedMovie.title}</h3>
                                        <div className="stars">{[1,2,3,4,5].map(s=><span key={s} className={`star ${s<=newReviewRating?'active':''}`} onClick={()=>setNewReviewRating(s)}>★</span>)}</div>
                                        <textarea className="comment-area" placeholder="Comentário..." value={newReviewComment} onChange={e=>setNewReviewComment(e.target.value)}/>
                                        <div style={{display:'flex', gap:'10px'}}><button className="primary-btn" onClick={submitReview} style={{marginTop:0}}>Salvar</button><button onClick={()=>setSelectedMovie(null)} style={{background:'none', border:'none', color:'red', cursor:'pointer'}}>X</button></div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                    <div>
                        <h3 className="section-title">Minha Coleção</h3>
                        <div className="movies-grid">
                            {userProfile.reviews && userProfile.reviews.map(rev => (
                                <div key={rev.id} className="movie-poster-card">
                                    <img src={rev.poster} className="movie-img"/>
                                    <div className="movie-rating-badge">★ {rev.rating}</div>
                                    <button className="delete-review-btn" onClick={()=>deleteReview(rev.id)}><TrashIcon/></button>
                                    {rev.comment && <div className="comment-tooltip"><strong>{rev.title}</strong><br/>"{rev.comment}"</div>}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
              </>
             )}
          </div>
        )}
      </div>
      
      <div className="bottom-nav">
        <div className={`nav-item ${currentView==='chat'?'active':''}`} onClick={()=>setCurrentView('chat')}>Chat</div>
        <div className={`nav-item ${currentView==='profile'?'active':''}`} onClick={()=>setCurrentView('profile')}>Perfil</div>
      </div>
    </div>
  );
}

export default App;