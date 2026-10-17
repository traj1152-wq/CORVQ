import {accessToken} from './auth.js';
export async function request(path, options = {}) {
  const token = await accessToken();
  const response = await fetch(`/api${path}`, {...options, headers: {'Content-Type': 'application/json', ...(token ? {Authorization:`Bearer ${token}`} : {}), ...options.headers}});
  if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail || 'Request failed')); }
  return response.json();
}
export const post = (path, body) => request(path, {method:'POST', body:JSON.stringify(body)});
export function graphLayout(graph) {
  return {nodes:graph.nodes.map((n,i)=>({id:n.id,data:{label:n.label},position:{x:300+240*Math.cos(i*2*Math.PI/graph.nodes.length),y:200+160*Math.sin(i*2*Math.PI/graph.nodes.length)},style:{background:'#fff',border:'1px solid #b9d2ce',borderRadius:10,padding:15,width:130,fontSize:11,color:'#163f39'}})), edges:graph.edges.map(e=>({...e, type:'default', markerEnd:{type:'arrowclosed',color:'#829b96'},style:{stroke:e.kind==='refund'?'#d0974b':'#829b96'},labelStyle:{fontSize:9,fill:'#627672'},labelBgStyle:{fill:'#f8faf9'},animated:false}))};
}
