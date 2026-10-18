import {accessToken} from './auth.js';
import {showcaseRequest} from './showcase.js';
export async function request(path, options = {}) {
  if (import.meta.env?.VITE_SHOWCASE === 'true') return showcaseRequest(path, options);
  const token = await accessToken();
  let response;
  try {
    response = await fetch(`/api${path}`, {...options, headers: {'Content-Type': 'application/json', ...(token ? {Authorization:`Bearer ${token}`} : {}), ...options.headers}});
  } catch {
    throw new Error('Cannot reach CORVQ. Check that the backend is running on port 8000.');
  }
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = body?.detail;
    const error = new Error(typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map(e => `${e.loc?.join('.') || 'Input'}: ${e.msg}`).join('; ') : `Request failed (${response.status}). Check the backend connection.`);
    error.status = response.status;
    throw error;
  }
  if (body === null) throw new Error('The server returned an invalid response. Check the API proxy configuration.');
  return body;
}
export const post = (path, body) => request(path, {method:'POST', body:JSON.stringify(body)});
export function graphLayout(graph) {
  return {nodes:graph.nodes.map((n,i)=>({id:n.id,data:{label:n.label},position:{x:300+240*Math.cos(i*2*Math.PI/graph.nodes.length),y:200+160*Math.sin(i*2*Math.PI/graph.nodes.length)},style:{background:'#fff',border:'1px solid #b9d2ce',borderRadius:10,padding:15,width:130,fontSize:11,color:'#163f39'}})), edges:graph.edges.map(e=>({...e, type:'default', markerEnd:{type:'arrowclosed',color:'#829b96'},style:{stroke:e.kind==='refund'?'#d0974b':'#829b96'},labelStyle:{fontSize:9,fill:'#627672'},labelBgStyle:{fill:'#f8faf9'},animated:false}))};
}
