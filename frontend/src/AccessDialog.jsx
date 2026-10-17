import React,{useState} from 'react';
import {X} from 'lucide-react';
import {signIn,signOut,sendVerification,firebaseEnabled} from './auth';
import {request} from './api';

export default function AccessDialog({onClose,onChange,mode='local'}){
 const useFirebase=mode==='firebase';
 const [error,setError]=useState(''),[busy,setBusy]=useState(false);
 const [verifyOnly,setVerifyOnly]=useState(false),[notice,setNotice]=useState('');
 const credentials=useFirebase||verifyOnly;
 async function submit(event){
  event.preventDefault();
  const form=new FormData(event.currentTarget);
  setBusy(true);setError('');setNotice('');
  try{
   if(verifyOnly){
    await sendVerification(form.get('email'),form.get('password'));
    event.target.reset();
    setNotice('Verification email requested. Open the link in your inbox, then sign in again.');
    return;
   }
   if(useFirebase)await signIn(form.get('email'),form.get('password'));
   else sessionStorage.setItem('corvq-token',form.get('token'));
   const user=await request('/me');
   await onChange(user);onClose();
  }catch(err){signOut();setError(err.message);}
  finally{setBusy(false);}
 }
 return <div className="modal-backdrop"><section className="modal panel" role="dialog" aria-modal="true" aria-label="Workspace access">
  <div className="panel-heading"><div><h2>{verifyOnly?'Verify Firebase email':'Workspace access'}</h2><p>{verifyOnly?'Use the Firebase account you just created.':useFirebase?'Sign in with your assigned account.':'Local development mode · no account login required.'}</p></div><button aria-label="Close access" onClick={onClose} disabled={busy}><X size={18}/></button></div>
  <form className="form" onSubmit={submit}>
   {credentials?<><label>Email<input name="email" type="email" autoComplete="username" required/></label><label>Password<input name="password" type="password" autoComplete="current-password" required/></label></>:<label>Development API token<input name="token" type="password" autoComplete="off" placeholder="Leave blank for local mode"/></label>}
   {error&&<div role="alert" className="alert error">{error}</div>}
   {notice&&<div role="status" className="alert">{notice}</div>}
   <div className="setup-actions"><button className="button primary" disabled={busy}>{busy?'Please wait…':verifyOnly?'Send verification email':'Continue'}</button>
   <button type="button" className="button secondary" disabled={busy} onClick={async()=>{signOut();try{await onChange(null);onClose();}catch(err){setError(err.message);}}}>Sign out</button></div>
   {firebaseEnabled()&&<button type="button" className="button secondary" disabled={busy} onClick={()=>{setVerifyOnly(!verifyOnly);setError('');setNotice('');}}>{verifyOnly?'Back to workspace access':'Verify Firebase email'}</button>}
  </form>
  <div className="panel-note">{credentials?'Credentials go directly to Firebase. Do not share your password in chat. Email verification does not grant CORVQ permissions; an administrator must assign your role.':'Leave the development token empty and click Continue. Firebase account setup can be completed separately before switching this backend to authenticated mode.'}</div>
 </section></div>;
}
