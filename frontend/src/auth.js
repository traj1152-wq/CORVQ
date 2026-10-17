// Firebase tokens stay in memory. Refresh tokens are never written to browser storage.
let session = null;
const key = () => import.meta.env?.VITE_FIREBASE_API_KEY;
export const firebaseEnabled = () => Boolean(key());
async function exchange(url, body, form = false) {
  const response = await fetch(url, {method:'POST',headers:{'Content-Type':form?'application/x-www-form-urlencoded':'application/json'},body:form?new URLSearchParams(body):JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) throw new Error('Sign-in failed or session expired. Check your account and try again.');
  return data;
}
export async function signIn(email,password) {
  if (!key()) throw new Error('Firebase sign-in is not configured for this frontend.');
  const data = await exchange(`https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=${encodeURIComponent(key())}`,{email,password,returnSecureToken:true});
  session={token:data.idToken,refresh:data.refreshToken,expires:Date.now()+Number(data.expiresIn)*1000};
  sessionStorage.removeItem('corvq-token');
}
export function signOut(){session=null;sessionStorage.removeItem('corvq-token');}
export async function accessToken(){
  if(!session) return sessionStorage.getItem('corvq-token');
  if(session.expires-Date.now()<60000){
    try{
      const data=await exchange(`https://securetoken.googleapis.com/v1/token?key=${encodeURIComponent(key())}`,{grant_type:'refresh_token',refresh_token:session.refresh},true);
      session={token:data.id_token,refresh:data.refresh_token,expires:Date.now()+Number(data.expires_in)*1000};
    }catch(e){signOut();throw e;}
  }
  return session.token;
}

