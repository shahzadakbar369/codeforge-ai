import { useState } from 'react';
export default function AuthPanel({api, onSuccess}) {
  const [signup, setSignup] = useState(false), [email, setEmail] = useState(''), [password, setPassword] = useState('');
  const [error, setError] = useState(''), [busy, setBusy] = useState(false);
  const [inviteCode, setInviteCode] = useState('');
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError('');
    try { onSuccess(await api(`/api/auth/${signup ? 'signup' : 'login'}`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password,invite_code:inviteCode})})); }
    catch(e) {setError(e.message);} finally {setBusy(false);}
  }
  return <main className="auth-shell"><section className="auth-card"><a className="brand" href="/">⌘ codeforge <span className="ai">AI</span></a><div className="eyebrow">YOUR PRIVATE MIGRATION WORKSPACE</div><h1>{signup ? 'Start your next chapter.' : 'Welcome back.'}</h1><p>Keep your projects, reports and migration history in one place.</p><form onSubmit={submit}><label htmlFor="email">Email address</label><input required name="email" id="email" type="email" maxLength={254} autoComplete="email" value={email} onChange={e=>setEmail(e.target.value)}/><label htmlFor="password">Password</label><input required name="password" id="password" type="password" minLength={10} maxLength={128} autoComplete={signup?'new-password':'current-password'} value={password} onChange={e=>setPassword(e.target.value)}/><small>Use 10 to 128 characters.</small>{signup && <><label htmlFor="invite-code">Invitation code (if provided by your host)</label><input id="invite-code" name="invite-code" maxLength={128} autoComplete="off" value={inviteCode} onChange={e=>setInviteCode(e.target.value)}/></>}{error && <p className="error" role="alert">{error}</p>}<button className="primary" disabled={busy}>{busy?'Please wait…':signup?'Create account':'Sign in'}</button></form><button className="text-button" disabled={busy} onClick={()=>{setSignup(!signup);setError('');}}>{signup?'Already have an account? Sign in':'New here? Create an account'}</button></section></main>;
}
