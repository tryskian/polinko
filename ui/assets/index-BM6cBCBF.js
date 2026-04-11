(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const r of document.querySelectorAll('link[rel="modulepreload"]'))n(r);new MutationObserver(r=>{for(const s of r)if(s.type==="childList")for(const a of s.addedNodes)a.tagName==="LINK"&&a.rel==="modulepreload"&&n(a)}).observe(document,{childList:!0,subtree:!0});function e(r){const s={};return r.integrity&&(s.integrity=r.integrity),r.referrerPolicy&&(s.referrerPolicy=r.referrerPolicy),r.crossOrigin==="use-credentials"?s.credentials="include":r.crossOrigin==="anonymous"?s.credentials="omit":s.credentials="same-origin",s}function n(r){if(r.ep)return;r.ep=!0;const s=e(r);fetch(r.href,s)}})();function qn(i){if(i===void 0)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return i}function wf(i,t){i.prototype=Object.create(t.prototype),i.prototype.constructor=i,i.__proto__=t}/*!
 * GSAP 3.14.2
 * https://gsap.com
 *
 * @license Copyright 2008-2025, GreenSock. All rights reserved.
 * Subject to the terms at https://gsap.com/standard-license
 * @author: Jack Doyle, jack@greensock.com
*/var Qe={autoSleep:120,force3D:"auto",nullTargetWarn:1,units:{lineHeight:""}},br={duration:.5,overwrite:!1,delay:0},tc,Re,ae,un=1e8,ie=1/un,Bo=Math.PI*2,kd=Bo/4,zd=0,Rf=Math.sqrt,Vd=Math.cos,Gd=Math.sin,be=function(t){return typeof t=="string"},fe=function(t){return typeof t=="function"},Qn=function(t){return typeof t=="number"},ec=function(t){return typeof t>"u"},In=function(t){return typeof t=="object"},ze=function(t){return t!==!1},nc=function(){return typeof window<"u"},Ps=function(t){return fe(t)||be(t)},Cf=typeof ArrayBuffer=="function"&&ArrayBuffer.isView||function(){},Ue=Array.isArray,Hd=/random\([^)]+\)/g,Wd=/,\s*/g,Xc=/(?:-?\.?\d|\.)+/gi,Pf=/[-+=.]*\d+[.e\-+]*\d*[e\-+]*\d*/g,gr=/[-+=.]*\d+[.e-]*\d*[a-z%]*/g,qa=/[-+=.]*\d+\.?\d*(?:e-|e\+)?\d*/gi,Df=/[+-]=-?[.\d]+/,Xd=/[^,'"\[\]\s]+/gi,qd=/^[+\-=e\s\d]*\d+[.\d]*([a-z]*|%)\s*$/i,le,En,ko,ic,en={},_a={},Lf,If=function(t){return(_a=Ar(t,en))&&Xe},rc=function(t,e){return console.warn("Invalid property",t,"set to",e,"Missing plugin? gsap.registerPlugin()")},as=function(t,e){return!e&&console.warn(t)},Uf=function(t,e){return t&&(en[t]=e)&&_a&&(_a[t]=e)||en},os=function(){return 0},Yd={suppressEvents:!0,isStart:!0,kill:!1},ra={suppressEvents:!0,kill:!1},$d={suppressEvents:!0},sc={},Mi=[],zo={},Nf,Ke={},Ya={},qc=30,sa=[],ac="",oc=function(t){var e=t[0],n,r;if(In(e)||fe(e)||(t=[t]),!(n=(e._gsap||{}).harness)){for(r=sa.length;r--&&!sa[r].targetTest(e););n=sa[r]}for(r=t.length;r--;)t[r]&&(t[r]._gsap||(t[r]._gsap=new sh(t[r],n)))||t.splice(r,1);return t},qi=function(t){return t._gsap||oc(fn(t))[0]._gsap},Ff=function(t,e,n){return(n=t[e])&&fe(n)?t[e]():ec(n)&&t.getAttribute&&t.getAttribute(e)||n},Ve=function(t,e){return(t=t.split(",")).forEach(e)||t},pe=function(t){return Math.round(t*1e5)/1e5||0},oe=function(t){return Math.round(t*1e7)/1e7||0},vr=function(t,e){var n=e.charAt(0),r=parseFloat(e.substr(2));return t=parseFloat(t),n==="+"?t+r:n==="-"?t-r:n==="*"?t*r:t/r},Kd=function(t,e){for(var n=e.length,r=0;t.indexOf(e[r])<0&&++r<n;);return r<n},ga=function(){var t=Mi.length,e=Mi.slice(0),n,r;for(zo={},Mi.length=0,n=0;n<t;n++)r=e[n],r&&r._lazy&&(r.render(r._lazy[0],r._lazy[1],!0)._lazy=0)},lc=function(t){return!!(t._initted||t._startAt||t.add)},Of=function(t,e,n,r){Mi.length&&!Re&&ga(),t.render(e,n,!!(Re&&e<0&&lc(t))),Mi.length&&!Re&&ga()},Bf=function(t){var e=parseFloat(t);return(e||e===0)&&(t+"").match(Xd).length<2?e:be(t)?t.trim():t},kf=function(t){return t},nn=function(t,e){for(var n in e)n in t||(t[n]=e[n]);return t},Zd=function(t){return function(e,n){for(var r in n)r in e||r==="duration"&&t||r==="ease"||(e[r]=n[r])}},Ar=function(t,e){for(var n in e)t[n]=e[n];return t},Yc=function i(t,e){for(var n in e)n!=="__proto__"&&n!=="constructor"&&n!=="prototype"&&(t[n]=In(e[n])?i(t[n]||(t[n]={}),e[n]):e[n]);return t},xa=function(t,e){var n={},r;for(r in t)r in e||(n[r]=t[r]);return n},is=function(t){var e=t.parent||le,n=t.keyframes?Zd(Ue(t.keyframes)):nn;if(ze(t.inherit))for(;e;)n(t,e.vars.defaults),e=e.parent||e._dp;return t},Jd=function(t,e){for(var n=t.length,r=n===e.length;r&&n--&&t[n]===e[n];);return n<0},zf=function(t,e,n,r,s){var a=t[r],o;if(s)for(o=e[s];a&&a[s]>o;)a=a._prev;return a?(e._next=a._next,a._next=e):(e._next=t[n],t[n]=e),e._next?e._next._prev=e:t[r]=e,e._prev=a,e.parent=e._dp=t,e},Ua=function(t,e,n,r){n===void 0&&(n="_first"),r===void 0&&(r="_last");var s=e._prev,a=e._next;s?s._next=a:t[n]===e&&(t[n]=a),a?a._prev=s:t[r]===e&&(t[r]=s),e._next=e._prev=e.parent=null},yi=function(t,e){t.parent&&(!e||t.parent.autoRemoveChildren)&&t.parent.remove&&t.parent.remove(t),t._act=0},Yi=function(t,e){if(t&&(!e||e._end>t._dur||e._start<0))for(var n=t;n;)n._dirty=1,n=n.parent;return t},jd=function(t){for(var e=t.parent;e&&e.parent;)e._dirty=1,e.totalDuration(),e=e.parent;return t},Vo=function(t,e,n,r){return t._startAt&&(Re?t._startAt.revert(ra):t.vars.immediateRender&&!t.vars.autoRevert||t._startAt.render(e,!0,r))},Qd=function i(t){return!t||t._ts&&i(t.parent)},$c=function(t){return t._repeat?wr(t._tTime,t=t.duration()+t._rDelay)*t:0},wr=function(t,e){var n=Math.floor(t=oe(t/e));return t&&n===t?n-1:n},va=function(t,e){return(t-e._start)*e._ts+(e._ts>=0?0:e._dirty?e.totalDuration():e._tDur)},Na=function(t){return t._end=oe(t._start+(t._tDur/Math.abs(t._ts||t._rts||ie)||0))},Fa=function(t,e){var n=t._dp;return n&&n.smoothChildTiming&&t._ts&&(t._start=oe(n._time-(t._ts>0?e/t._ts:((t._dirty?t.totalDuration():t._tDur)-e)/-t._ts)),Na(t),n._dirty||Yi(n,t)),t},Vf=function(t,e){var n;if((e._time||!e._dur&&e._initted||e._start<t._time&&(e._dur||!e.add))&&(n=va(t.rawTime(),e),(!e._dur||Ss(0,e.totalDuration(),n)-e._tTime>ie)&&e.render(n,!0)),Yi(t,e)._dp&&t._initted&&t._time>=t._dur&&t._ts){if(t._dur<t.duration())for(n=t;n._dp;)n.rawTime()>=0&&n.totalTime(n._tTime),n=n._dp;t._zTime=-ie}},bn=function(t,e,n,r){return e.parent&&yi(e),e._start=oe((Qn(n)?n:n||t!==le?an(t,n,e):t._time)+e._delay),e._end=oe(e._start+(e.totalDuration()/Math.abs(e.timeScale())||0)),zf(t,e,"_first","_last",t._sort?"_start":0),Go(e)||(t._recent=e),r||Vf(t,e),t._ts<0&&Fa(t,t._tTime),t},Gf=function(t,e){return(en.ScrollTrigger||rc("scrollTrigger",e))&&en.ScrollTrigger.create(e,t)},Hf=function(t,e,n,r,s){if(uc(t,e,s),!t._initted)return 1;if(!n&&t._pt&&!Re&&(t._dur&&t.vars.lazy!==!1||!t._dur&&t.vars.lazy)&&Nf!==Ze.frame)return Mi.push(t),t._lazy=[s,r],1},tp=function i(t){var e=t.parent;return e&&e._ts&&e._initted&&!e._lock&&(e.rawTime()<0||i(e))},Go=function(t){var e=t.data;return e==="isFromStart"||e==="isStart"},ep=function(t,e,n,r){var s=t.ratio,a=e<0||!e&&(!t._start&&tp(t)&&!(!t._initted&&Go(t))||(t._ts<0||t._dp._ts<0)&&!Go(t))?0:1,o=t._rDelay,l=0,c,u,h;if(o&&t._repeat&&(l=Ss(0,t._tDur,e),u=wr(l,o),t._yoyo&&u&1&&(a=1-a),u!==wr(t._tTime,o)&&(s=1-a,t.vars.repeatRefresh&&t._initted&&t.invalidate())),a!==s||Re||r||t._zTime===ie||!e&&t._zTime){if(!t._initted&&Hf(t,e,r,n,l))return;for(h=t._zTime,t._zTime=e||(n?ie:0),n||(n=e&&!h),t.ratio=a,t._from&&(a=1-a),t._time=0,t._tTime=l,c=t._pt;c;)c.r(a,c.d),c=c._next;e<0&&Vo(t,e,n,!0),t._onUpdate&&!n&&Je(t,"onUpdate"),l&&t._repeat&&!n&&t.parent&&Je(t,"onRepeat"),(e>=t._tDur||e<0)&&t.ratio===a&&(a&&yi(t,1),!n&&!Re&&(Je(t,a?"onComplete":"onReverseComplete",!0),t._prom&&t._prom()))}else t._zTime||(t._zTime=e)},np=function(t,e,n){var r;if(n>e)for(r=t._first;r&&r._start<=n;){if(r.data==="isPause"&&r._start>e)return r;r=r._next}else for(r=t._last;r&&r._start>=n;){if(r.data==="isPause"&&r._start<e)return r;r=r._prev}},Rr=function(t,e,n,r){var s=t._repeat,a=oe(e)||0,o=t._tTime/t._tDur;return o&&!r&&(t._time*=a/t._dur),t._dur=a,t._tDur=s?s<0?1e10:oe(a*(s+1)+t._rDelay*s):a,o>0&&!r&&Fa(t,t._tTime=t._tDur*o),t.parent&&Na(t),n||Yi(t.parent,t),t},Kc=function(t){return t instanceof Fe?Yi(t):Rr(t,t._dur)},ip={_start:0,endTime:os,totalDuration:os},an=function i(t,e,n){var r=t.labels,s=t._recent||ip,a=t.duration()>=un?s.endTime(!1):t._dur,o,l,c;return be(e)&&(isNaN(e)||e in r)?(l=e.charAt(0),c=e.substr(-1)==="%",o=e.indexOf("="),l==="<"||l===">"?(o>=0&&(e=e.replace(/=/,"")),(l==="<"?s._start:s.endTime(s._repeat>=0))+(parseFloat(e.substr(1))||0)*(c?(o<0?s:n).totalDuration()/100:1)):o<0?(e in r||(r[e]=a),r[e]):(l=parseFloat(e.charAt(o-1)+e.substr(o+1)),c&&n&&(l=l/100*(Ue(n)?n[0]:n).totalDuration()),o>1?i(t,e.substr(0,o-1),n)+l:a+l)):e==null?a:+e},rs=function(t,e,n){var r=Qn(e[1]),s=(r?2:1)+(t<2?0:1),a=e[s],o,l;if(r&&(a.duration=e[1]),a.parent=n,t){for(o=a,l=n;l&&!("immediateRender"in o);)o=l.vars.defaults||{},l=ze(l.vars.inherit)&&l.parent;a.immediateRender=ze(o.immediateRender),t<2?a.runBackwards=1:a.startAt=e[s-1]}return new xe(e[0],a,e[s+1])},Ai=function(t,e){return t||t===0?e(t):e},Ss=function(t,e,n){return n<t?t:n>e?e:n},Le=function(t,e){return!be(t)||!(e=qd.exec(t))?"":e[1]},rp=function(t,e,n){return Ai(n,function(r){return Ss(t,e,r)})},Ho=[].slice,Wf=function(t,e){return t&&In(t)&&"length"in t&&(!e&&!t.length||t.length-1 in t&&In(t[0]))&&!t.nodeType&&t!==En},sp=function(t,e,n){return n===void 0&&(n=[]),t.forEach(function(r){var s;return be(r)&&!e||Wf(r,1)?(s=n).push.apply(s,fn(r)):n.push(r)})||n},fn=function(t,e,n){return ae&&!e&&ae.selector?ae.selector(t):be(t)&&!n&&(ko||!Cr())?Ho.call((e||ic).querySelectorAll(t),0):Ue(t)?sp(t,n):Wf(t)?Ho.call(t,0):t?[t]:[]},Wo=function(t){return t=fn(t)[0]||as("Invalid scope")||{},function(e){var n=t.current||t.nativeElement||t;return fn(e,n.querySelectorAll?n:n===t?as("Invalid scope")||ic.createElement("div"):t)}},Xf=function(t){return t.sort(function(){return .5-Math.random()})},qf=function(t){if(fe(t))return t;var e=In(t)?t:{each:t},n=$i(e.ease),r=e.from||0,s=parseFloat(e.base)||0,a={},o=r>0&&r<1,l=isNaN(r)||o,c=e.axis,u=r,h=r;return be(r)?u=h={center:.5,edges:.5,end:1}[r]||0:!o&&l&&(u=r[0],h=r[1]),function(f,d,_){var g=(_||e).length,p=a[g],m,M,T,S,b,A,R,x,y;if(!p){if(y=e.grid==="auto"?0:(e.grid||[1,un])[1],!y){for(R=-un;R<(R=_[y++].getBoundingClientRect().left)&&y<g;);y<g&&y--}for(p=a[g]=[],m=l?Math.min(y,g)*u-.5:r%y,M=y===un?0:l?g*h/y-.5:r/y|0,R=0,x=un,A=0;A<g;A++)T=A%y-m,S=M-(A/y|0),p[A]=b=c?Math.abs(c==="y"?S:T):Rf(T*T+S*S),b>R&&(R=b),b<x&&(x=b);r==="random"&&Xf(p),p.max=R-x,p.min=x,p.v=g=(parseFloat(e.amount)||parseFloat(e.each)*(y>g?g-1:c?c==="y"?g/y:y:Math.max(y,g/y))||0)*(r==="edges"?-1:1),p.b=g<0?s-g:s,p.u=Le(e.amount||e.each)||0,n=n&&g<0?nh(n):n}return g=(p[f]-p.min)/p.max||0,oe(p.b+(n?n(g):g)*p.v)+p.u}},Xo=function(t){var e=Math.pow(10,((t+"").split(".")[1]||"").length);return function(n){var r=oe(Math.round(parseFloat(n)/t)*t*e);return(r-r%1)/e+(Qn(n)?0:Le(n))}},Yf=function(t,e){var n=Ue(t),r,s;return!n&&In(t)&&(r=n=t.radius||un,t.values?(t=fn(t.values),(s=!Qn(t[0]))&&(r*=r)):t=Xo(t.increment)),Ai(e,n?fe(t)?function(a){return s=t(a),Math.abs(s-a)<=r?s:a}:function(a){for(var o=parseFloat(s?a.x:a),l=parseFloat(s?a.y:0),c=un,u=0,h=t.length,f,d;h--;)s?(f=t[h].x-o,d=t[h].y-l,f=f*f+d*d):f=Math.abs(t[h]-o),f<c&&(c=f,u=h);return u=!r||c<=r?t[u]:a,s||u===a||Qn(a)?u:u+Le(a)}:Xo(t))},$f=function(t,e,n,r){return Ai(Ue(t)?!e:n===!0?!!(n=0):!r,function(){return Ue(t)?t[~~(Math.random()*t.length)]:(n=n||1e-5)&&(r=n<1?Math.pow(10,(n+"").length-2):1)&&Math.floor(Math.round((t-n/2+Math.random()*(e-t+n*.99))/n)*n*r)/r})},ap=function(){for(var t=arguments.length,e=new Array(t),n=0;n<t;n++)e[n]=arguments[n];return function(r){return e.reduce(function(s,a){return a(s)},r)}},op=function(t,e){return function(n){return t(parseFloat(n))+(e||Le(n))}},lp=function(t,e,n){return Zf(t,e,0,1,n)},Kf=function(t,e,n){return Ai(n,function(r){return t[~~e(r)]})},cp=function i(t,e,n){var r=e-t;return Ue(t)?Kf(t,i(0,t.length),e):Ai(n,function(s){return(r+(s-t)%r)%r+t})},up=function i(t,e,n){var r=e-t,s=r*2;return Ue(t)?Kf(t,i(0,t.length-1),e):Ai(n,function(a){return a=(s+(a-t)%s)%s||0,t+(a>r?s-a:a)})},ls=function(t){return t.replace(Hd,function(e){var n=e.indexOf("[")+1,r=e.substring(n||7,n?e.indexOf("]"):e.length-1).split(Wd);return $f(n?r:+r[0],n?0:+r[1],+r[2]||1e-5)})},Zf=function(t,e,n,r,s){var a=e-t,o=r-n;return Ai(s,function(l){return n+((l-t)/a*o||0)})},fp=function i(t,e,n,r){var s=isNaN(t+e)?0:function(d){return(1-d)*t+d*e};if(!s){var a=be(t),o={},l,c,u,h,f;if(n===!0&&(r=1)&&(n=null),a)t={p:t},e={p:e};else if(Ue(t)&&!Ue(e)){for(u=[],h=t.length,f=h-2,c=1;c<h;c++)u.push(i(t[c-1],t[c]));h--,s=function(_){_*=h;var g=Math.min(f,~~_);return u[g](_-g)},n=e}else r||(t=Ar(Ue(t)?[]:{},t));if(!u){for(l in e)cc.call(o,t,l,"get",e[l]);s=function(_){return dc(_,o)||(a?t.p:t)}}}return Ai(n,s)},Zc=function(t,e,n){var r=t.labels,s=un,a,o,l;for(a in r)o=r[a]-e,o<0==!!n&&o&&s>(o=Math.abs(o))&&(l=a,s=o);return l},Je=function(t,e,n){var r=t.vars,s=r[e],a=ae,o=t._ctx,l,c,u;if(s)return l=r[e+"Params"],c=r.callbackScope||t,n&&Mi.length&&ga(),o&&(ae=o),u=l?s.apply(c,l):s.call(c),ae=a,u},Zr=function(t){return yi(t),t.scrollTrigger&&t.scrollTrigger.kill(!!Re),t.progress()<1&&Je(t,"onInterrupt"),t},xr,Jf=[],jf=function(t){if(t)if(t=!t.name&&t.default||t,nc()||t.headless){var e=t.name,n=fe(t),r=e&&!n&&t.init?function(){this._props=[]}:t,s={init:os,render:dc,add:cc,kill:wp,modifier:Ap,rawVars:0},a={targetTest:0,get:0,getSetter:hc,aliases:{},register:0};if(Cr(),t!==r){if(Ke[e])return;nn(r,nn(xa(t,s),a)),Ar(r.prototype,Ar(s,xa(t,a))),Ke[r.prop=e]=r,t.targetTest&&(sa.push(r),sc[e]=1),e=(e==="css"?"CSS":e.charAt(0).toUpperCase()+e.substr(1))+"Plugin"}Uf(e,r),t.register&&t.register(Xe,r,Ge)}else Jf.push(t)},ne=255,Jr={aqua:[0,ne,ne],lime:[0,ne,0],silver:[192,192,192],black:[0,0,0],maroon:[128,0,0],teal:[0,128,128],blue:[0,0,ne],navy:[0,0,128],white:[ne,ne,ne],olive:[128,128,0],yellow:[ne,ne,0],orange:[ne,165,0],gray:[128,128,128],purple:[128,0,128],green:[0,128,0],red:[ne,0,0],pink:[ne,192,203],cyan:[0,ne,ne],transparent:[ne,ne,ne,0]},$a=function(t,e,n){return t+=t<0?1:t>1?-1:0,(t*6<1?e+(n-e)*t*6:t<.5?n:t*3<2?e+(n-e)*(2/3-t)*6:e)*ne+.5|0},Qf=function(t,e,n){var r=t?Qn(t)?[t>>16,t>>8&ne,t&ne]:0:Jr.black,s,a,o,l,c,u,h,f,d,_;if(!r){if(t.substr(-1)===","&&(t=t.substr(0,t.length-1)),Jr[t])r=Jr[t];else if(t.charAt(0)==="#"){if(t.length<6&&(s=t.charAt(1),a=t.charAt(2),o=t.charAt(3),t="#"+s+s+a+a+o+o+(t.length===5?t.charAt(4)+t.charAt(4):"")),t.length===9)return r=parseInt(t.substr(1,6),16),[r>>16,r>>8&ne,r&ne,parseInt(t.substr(7),16)/255];t=parseInt(t.substr(1),16),r=[t>>16,t>>8&ne,t&ne]}else if(t.substr(0,3)==="hsl"){if(r=_=t.match(Xc),!e)l=+r[0]%360/360,c=+r[1]/100,u=+r[2]/100,a=u<=.5?u*(c+1):u+c-u*c,s=u*2-a,r.length>3&&(r[3]*=1),r[0]=$a(l+1/3,s,a),r[1]=$a(l,s,a),r[2]=$a(l-1/3,s,a);else if(~t.indexOf("="))return r=t.match(Pf),n&&r.length<4&&(r[3]=1),r}else r=t.match(Xc)||Jr.transparent;r=r.map(Number)}return e&&!_&&(s=r[0]/ne,a=r[1]/ne,o=r[2]/ne,h=Math.max(s,a,o),f=Math.min(s,a,o),u=(h+f)/2,h===f?l=c=0:(d=h-f,c=u>.5?d/(2-h-f):d/(h+f),l=h===s?(a-o)/d+(a<o?6:0):h===a?(o-s)/d+2:(s-a)/d+4,l*=60),r[0]=~~(l+.5),r[1]=~~(c*100+.5),r[2]=~~(u*100+.5)),n&&r.length<4&&(r[3]=1),r},th=function(t){var e=[],n=[],r=-1;return t.split(Si).forEach(function(s){var a=s.match(gr)||[];e.push.apply(e,a),n.push(r+=a.length+1)}),e.c=n,e},Jc=function(t,e,n){var r="",s=(t+r).match(Si),a=e?"hsla(":"rgba(",o=0,l,c,u,h;if(!s)return t;if(s=s.map(function(f){return(f=Qf(f,e,1))&&a+(e?f[0]+","+f[1]+"%,"+f[2]+"%,"+f[3]:f.join(","))+")"}),n&&(u=th(t),l=n.c,l.join(r)!==u.c.join(r)))for(c=t.replace(Si,"1").split(gr),h=c.length-1;o<h;o++)r+=c[o]+(~l.indexOf(o)?s.shift()||a+"0,0,0,0)":(u.length?u:s.length?s:n).shift());if(!c)for(c=t.split(Si),h=c.length-1;o<h;o++)r+=c[o]+s[o];return r+c[h]},Si=function(){var i="(?:\\b(?:(?:rgb|rgba|hsl|hsla)\\(.+?\\))|\\B#(?:[0-9a-f]{3,4}){1,2}\\b",t;for(t in Jr)i+="|"+t+"\\b";return new RegExp(i+")","gi")}(),hp=/hsl[a]?\(/,eh=function(t){var e=t.join(" "),n;if(Si.lastIndex=0,Si.test(e))return n=hp.test(e),t[1]=Jc(t[1],n),t[0]=Jc(t[0],n,th(t[1])),!0},cs,Ze=function(){var i=Date.now,t=500,e=33,n=i(),r=n,s=1e3/240,a=s,o=[],l,c,u,h,f,d,_=function g(p){var m=i()-r,M=p===!0,T,S,b,A;if((m>t||m<0)&&(n+=m-e),r+=m,b=r-n,T=b-a,(T>0||M)&&(A=++h.frame,f=b-h.time*1e3,h.time=b=b/1e3,a+=T+(T>=s?4:s-T),S=1),M||(l=c(g)),S)for(d=0;d<o.length;d++)o[d](b,f,A,p)};return h={time:0,frame:0,tick:function(){_(!0)},deltaRatio:function(p){return f/(1e3/(p||60))},wake:function(){Lf&&(!ko&&nc()&&(En=ko=window,ic=En.document||{},en.gsap=Xe,(En.gsapVersions||(En.gsapVersions=[])).push(Xe.version),If(_a||En.GreenSockGlobals||!En.gsap&&En||{}),Jf.forEach(jf)),u=typeof requestAnimationFrame<"u"&&requestAnimationFrame,l&&h.sleep(),c=u||function(p){return setTimeout(p,a-h.time*1e3+1|0)},cs=1,_(2))},sleep:function(){(u?cancelAnimationFrame:clearTimeout)(l),cs=0,c=os},lagSmoothing:function(p,m){t=p||1/0,e=Math.min(m||33,t)},fps:function(p){s=1e3/(p||240),a=h.time*1e3+s},add:function(p,m,M){var T=m?function(S,b,A,R){p(S,b,A,R),h.remove(T)}:p;return h.remove(p),o[M?"unshift":"push"](T),Cr(),T},remove:function(p,m){~(m=o.indexOf(p))&&o.splice(m,1)&&d>=m&&d--},_listeners:o},h}(),Cr=function(){return!cs&&Ze.wake()},Vt={},dp=/^[\d.\-M][\d.\-,\s]/,pp=/["']/g,mp=function(t){for(var e={},n=t.substr(1,t.length-3).split(":"),r=n[0],s=1,a=n.length,o,l,c;s<a;s++)l=n[s],o=s!==a-1?l.lastIndexOf(","):l.length,c=l.substr(0,o),e[r]=isNaN(c)?c.replace(pp,"").trim():+c,r=l.substr(o+1).trim();return e},_p=function(t){var e=t.indexOf("(")+1,n=t.indexOf(")"),r=t.indexOf("(",e);return t.substring(e,~r&&r<n?t.indexOf(")",n+1):n)},gp=function(t){var e=(t+"").split("("),n=Vt[e[0]];return n&&e.length>1&&n.config?n.config.apply(null,~t.indexOf("{")?[mp(e[1])]:_p(t).split(",").map(Bf)):Vt._CE&&dp.test(t)?Vt._CE("",t):n},nh=function(t){return function(e){return 1-t(1-e)}},ih=function i(t,e){for(var n=t._first,r;n;)n instanceof Fe?i(n,e):n.vars.yoyoEase&&(!n._yoyo||!n._repeat)&&n._yoyo!==e&&(n.timeline?i(n.timeline,e):(r=n._ease,n._ease=n._yEase,n._yEase=r,n._yoyo=e)),n=n._next},$i=function(t,e){return t&&(fe(t)?t:Vt[t]||gp(t))||e},Qi=function(t,e,n,r){n===void 0&&(n=function(l){return 1-e(1-l)}),r===void 0&&(r=function(l){return l<.5?e(l*2)/2:1-e((1-l)*2)/2});var s={easeIn:e,easeOut:n,easeInOut:r},a;return Ve(t,function(o){Vt[o]=en[o]=s,Vt[a=o.toLowerCase()]=n;for(var l in s)Vt[a+(l==="easeIn"?".in":l==="easeOut"?".out":".inOut")]=Vt[o+"."+l]=s[l]}),s},rh=function(t){return function(e){return e<.5?(1-t(1-e*2))/2:.5+t((e-.5)*2)/2}},Ka=function i(t,e,n){var r=e>=1?e:1,s=(n||(t?.3:.45))/(e<1?e:1),a=s/Bo*(Math.asin(1/r)||0),o=function(u){return u===1?1:r*Math.pow(2,-10*u)*Gd((u-a)*s)+1},l=t==="out"?o:t==="in"?function(c){return 1-o(1-c)}:rh(o);return s=Bo/s,l.config=function(c,u){return i(t,c,u)},l},Za=function i(t,e){e===void 0&&(e=1.70158);var n=function(a){return a?--a*a*((e+1)*a+e)+1:0},r=t==="out"?n:t==="in"?function(s){return 1-n(1-s)}:rh(n);return r.config=function(s){return i(t,s)},r};Ve("Linear,Quad,Cubic,Quart,Quint,Strong",function(i,t){var e=t<5?t+1:t;Qi(i+",Power"+(e-1),t?function(n){return Math.pow(n,e)}:function(n){return n},function(n){return 1-Math.pow(1-n,e)},function(n){return n<.5?Math.pow(n*2,e)/2:1-Math.pow((1-n)*2,e)/2})});Vt.Linear.easeNone=Vt.none=Vt.Linear.easeIn;Qi("Elastic",Ka("in"),Ka("out"),Ka());(function(i,t){var e=1/t,n=2*e,r=2.5*e,s=function(o){return o<e?i*o*o:o<n?i*Math.pow(o-1.5/t,2)+.75:o<r?i*(o-=2.25/t)*o+.9375:i*Math.pow(o-2.625/t,2)+.984375};Qi("Bounce",function(a){return 1-s(1-a)},s)})(7.5625,2.75);Qi("Expo",function(i){return Math.pow(2,10*(i-1))*i+i*i*i*i*i*i*(1-i)});Qi("Circ",function(i){return-(Rf(1-i*i)-1)});Qi("Sine",function(i){return i===1?1:-Vd(i*kd)+1});Qi("Back",Za("in"),Za("out"),Za());Vt.SteppedEase=Vt.steps=en.SteppedEase={config:function(t,e){t===void 0&&(t=1);var n=1/t,r=t+(e?0:1),s=e?1:0,a=1-ie;return function(o){return((r*Ss(0,a,o)|0)+s)*n}}};br.ease=Vt["quad.out"];Ve("onComplete,onUpdate,onStart,onRepeat,onReverseComplete,onInterrupt",function(i){return ac+=i+","+i+"Params,"});var sh=function(t,e){this.id=zd++,t._gsap=this,this.target=t,this.harness=e,this.get=e?e.get:Ff,this.set=e?e.getSetter:hc},us=function(){function i(e){this.vars=e,this._delay=+e.delay||0,(this._repeat=e.repeat===1/0?-2:e.repeat||0)&&(this._rDelay=e.repeatDelay||0,this._yoyo=!!e.yoyo||!!e.yoyoEase),this._ts=1,Rr(this,+e.duration,1,1),this.data=e.data,ae&&(this._ctx=ae,ae.data.push(this)),cs||Ze.wake()}var t=i.prototype;return t.delay=function(n){return n||n===0?(this.parent&&this.parent.smoothChildTiming&&this.startTime(this._start+n-this._delay),this._delay=n,this):this._delay},t.duration=function(n){return arguments.length?this.totalDuration(this._repeat>0?n+(n+this._rDelay)*this._repeat:n):this.totalDuration()&&this._dur},t.totalDuration=function(n){return arguments.length?(this._dirty=0,Rr(this,this._repeat<0?n:(n-this._repeat*this._rDelay)/(this._repeat+1))):this._tDur},t.totalTime=function(n,r){if(Cr(),!arguments.length)return this._tTime;var s=this._dp;if(s&&s.smoothChildTiming&&this._ts){for(Fa(this,n),!s._dp||s.parent||Vf(s,this);s&&s.parent;)s.parent._time!==s._start+(s._ts>=0?s._tTime/s._ts:(s.totalDuration()-s._tTime)/-s._ts)&&s.totalTime(s._tTime,!0),s=s.parent;!this.parent&&this._dp.autoRemoveChildren&&(this._ts>0&&n<this._tDur||this._ts<0&&n>0||!this._tDur&&!n)&&bn(this._dp,this,this._start-this._delay)}return(this._tTime!==n||!this._dur&&!r||this._initted&&Math.abs(this._zTime)===ie||!this._initted&&this._dur&&n||!n&&!this._initted&&(this.add||this._ptLookup))&&(this._ts||(this._pTime=n),Of(this,n,r)),this},t.time=function(n,r){return arguments.length?this.totalTime(Math.min(this.totalDuration(),n+$c(this))%(this._dur+this._rDelay)||(n?this._dur:0),r):this._time},t.totalProgress=function(n,r){return arguments.length?this.totalTime(this.totalDuration()*n,r):this.totalDuration()?Math.min(1,this._tTime/this._tDur):this.rawTime()>=0&&this._initted?1:0},t.progress=function(n,r){return arguments.length?this.totalTime(this.duration()*(this._yoyo&&!(this.iteration()&1)?1-n:n)+$c(this),r):this.duration()?Math.min(1,this._time/this._dur):this.rawTime()>0?1:0},t.iteration=function(n,r){var s=this.duration()+this._rDelay;return arguments.length?this.totalTime(this._time+(n-1)*s,r):this._repeat?wr(this._tTime,s)+1:1},t.timeScale=function(n,r){if(!arguments.length)return this._rts===-ie?0:this._rts;if(this._rts===n)return this;var s=this.parent&&this._ts?va(this.parent._time,this):this._tTime;return this._rts=+n||0,this._ts=this._ps||n===-ie?0:this._rts,this.totalTime(Ss(-Math.abs(this._delay),this.totalDuration(),s),r!==!1),Na(this),jd(this)},t.paused=function(n){return arguments.length?(this._ps!==n&&(this._ps=n,n?(this._pTime=this._tTime||Math.max(-this._delay,this.rawTime()),this._ts=this._act=0):(Cr(),this._ts=this._rts,this.totalTime(this.parent&&!this.parent.smoothChildTiming?this.rawTime():this._tTime||this._pTime,this.progress()===1&&Math.abs(this._zTime)!==ie&&(this._tTime-=ie)))),this):this._ps},t.startTime=function(n){if(arguments.length){this._start=oe(n);var r=this.parent||this._dp;return r&&(r._sort||!this.parent)&&bn(r,this,this._start-this._delay),this}return this._start},t.endTime=function(n){return this._start+(ze(n)?this.totalDuration():this.duration())/Math.abs(this._ts||1)},t.rawTime=function(n){var r=this.parent||this._dp;return r?n&&(!this._ts||this._repeat&&this._time&&this.totalProgress()<1)?this._tTime%(this._dur+this._rDelay):this._ts?va(r.rawTime(n),this):this._tTime:this._tTime},t.revert=function(n){n===void 0&&(n=$d);var r=Re;return Re=n,lc(this)&&(this.timeline&&this.timeline.revert(n),this.totalTime(-.01,n.suppressEvents)),this.data!=="nested"&&n.kill!==!1&&this.kill(),Re=r,this},t.globalTime=function(n){for(var r=this,s=arguments.length?n:r.rawTime();r;)s=r._start+s/(Math.abs(r._ts)||1),r=r._dp;return!this.parent&&this._sat?this._sat.globalTime(n):s},t.repeat=function(n){return arguments.length?(this._repeat=n===1/0?-2:n,Kc(this)):this._repeat===-2?1/0:this._repeat},t.repeatDelay=function(n){if(arguments.length){var r=this._time;return this._rDelay=n,Kc(this),r?this.time(r):this}return this._rDelay},t.yoyo=function(n){return arguments.length?(this._yoyo=n,this):this._yoyo},t.seek=function(n,r){return this.totalTime(an(this,n),ze(r))},t.restart=function(n,r){return this.play().totalTime(n?-this._delay:0,ze(r)),this._dur||(this._zTime=-ie),this},t.play=function(n,r){return n!=null&&this.seek(n,r),this.reversed(!1).paused(!1)},t.reverse=function(n,r){return n!=null&&this.seek(n||this.totalDuration(),r),this.reversed(!0).paused(!1)},t.pause=function(n,r){return n!=null&&this.seek(n,r),this.paused(!0)},t.resume=function(){return this.paused(!1)},t.reversed=function(n){return arguments.length?(!!n!==this.reversed()&&this.timeScale(-this._rts||(n?-ie:0)),this):this._rts<0},t.invalidate=function(){return this._initted=this._act=0,this._zTime=-ie,this},t.isActive=function(){var n=this.parent||this._dp,r=this._start,s;return!!(!n||this._ts&&this._initted&&n.isActive()&&(s=n.rawTime(!0))>=r&&s<this.endTime(!0)-ie)},t.eventCallback=function(n,r,s){var a=this.vars;return arguments.length>1?(r?(a[n]=r,s&&(a[n+"Params"]=s),n==="onUpdate"&&(this._onUpdate=r)):delete a[n],this):a[n]},t.then=function(n){var r=this,s=r._prom;return new Promise(function(a){var o=fe(n)?n:kf,l=function(){var u=r.then;r.then=null,s&&s(),fe(o)&&(o=o(r))&&(o.then||o===r)&&(r.then=u),a(o),r.then=u};r._initted&&r.totalProgress()===1&&r._ts>=0||!r._tTime&&r._ts<0?l():r._prom=l})},t.kill=function(){Zr(this)},i}();nn(us.prototype,{_time:0,_start:0,_end:0,_tTime:0,_tDur:0,_dirty:0,_repeat:0,_yoyo:!1,parent:null,_initted:!1,_rDelay:0,_ts:1,_dp:0,ratio:0,_zTime:-ie,_prom:0,_ps:!1,_rts:1});var Fe=function(i){wf(t,i);function t(n,r){var s;return n===void 0&&(n={}),s=i.call(this,n)||this,s.labels={},s.smoothChildTiming=!!n.smoothChildTiming,s.autoRemoveChildren=!!n.autoRemoveChildren,s._sort=ze(n.sortChildren),le&&bn(n.parent||le,qn(s),r),n.reversed&&s.reverse(),n.paused&&s.paused(!0),n.scrollTrigger&&Gf(qn(s),n.scrollTrigger),s}var e=t.prototype;return e.to=function(r,s,a){return rs(0,arguments,this),this},e.from=function(r,s,a){return rs(1,arguments,this),this},e.fromTo=function(r,s,a,o){return rs(2,arguments,this),this},e.set=function(r,s,a){return s.duration=0,s.parent=this,is(s).repeatDelay||(s.repeat=0),s.immediateRender=!!s.immediateRender,new xe(r,s,an(this,a),1),this},e.call=function(r,s,a){return bn(this,xe.delayedCall(0,r,s),a)},e.staggerTo=function(r,s,a,o,l,c,u){return a.duration=s,a.stagger=a.stagger||o,a.onComplete=c,a.onCompleteParams=u,a.parent=this,new xe(r,a,an(this,l)),this},e.staggerFrom=function(r,s,a,o,l,c,u){return a.runBackwards=1,is(a).immediateRender=ze(a.immediateRender),this.staggerTo(r,s,a,o,l,c,u)},e.staggerFromTo=function(r,s,a,o,l,c,u,h){return o.startAt=a,is(o).immediateRender=ze(o.immediateRender),this.staggerTo(r,s,o,l,c,u,h)},e.render=function(r,s,a){var o=this._time,l=this._dirty?this.totalDuration():this._tDur,c=this._dur,u=r<=0?0:oe(r),h=this._zTime<0!=r<0&&(this._initted||!c),f,d,_,g,p,m,M,T,S,b,A,R;if(this!==le&&u>l&&r>=0&&(u=l),u!==this._tTime||a||h){if(o!==this._time&&c&&(u+=this._time-o,r+=this._time-o),f=u,S=this._start,T=this._ts,m=!T,h&&(c||(o=this._zTime),(r||!s)&&(this._zTime=r)),this._repeat){if(A=this._yoyo,p=c+this._rDelay,this._repeat<-1&&r<0)return this.totalTime(p*100+r,s,a);if(f=oe(u%p),u===l?(g=this._repeat,f=c):(b=oe(u/p),g=~~b,g&&g===b&&(f=c,g--),f>c&&(f=c)),b=wr(this._tTime,p),!o&&this._tTime&&b!==g&&this._tTime-b*p-this._dur<=0&&(b=g),A&&g&1&&(f=c-f,R=1),g!==b&&!this._lock){var x=A&&b&1,y=x===(A&&g&1);if(g<b&&(x=!x),o=x?0:u%c?c:u,this._lock=1,this.render(o||(R?0:oe(g*p)),s,!c)._lock=0,this._tTime=u,!s&&this.parent&&Je(this,"onRepeat"),this.vars.repeatRefresh&&!R&&(this.invalidate()._lock=1,b=g),o&&o!==this._time||m!==!this._ts||this.vars.onRepeat&&!this.parent&&!this._act)return this;if(c=this._dur,l=this._tDur,y&&(this._lock=2,o=x?c:-1e-4,this.render(o,!0),this.vars.repeatRefresh&&!R&&this.invalidate()),this._lock=0,!this._ts&&!m)return this;ih(this,R)}}if(this._hasPause&&!this._forcing&&this._lock<2&&(M=np(this,oe(o),oe(f)),M&&(u-=f-(f=M._start))),this._tTime=u,this._time=f,this._act=!T,this._initted||(this._onUpdate=this.vars.onUpdate,this._initted=1,this._zTime=r,o=0),!o&&u&&c&&!s&&!b&&(Je(this,"onStart"),this._tTime!==u))return this;if(f>=o&&r>=0)for(d=this._first;d;){if(_=d._next,(d._act||f>=d._start)&&d._ts&&M!==d){if(d.parent!==this)return this.render(r,s,a);if(d.render(d._ts>0?(f-d._start)*d._ts:(d._dirty?d.totalDuration():d._tDur)+(f-d._start)*d._ts,s,a),f!==this._time||!this._ts&&!m){M=0,_&&(u+=this._zTime=-ie);break}}d=_}else{d=this._last;for(var G=r<0?r:f;d;){if(_=d._prev,(d._act||G<=d._end)&&d._ts&&M!==d){if(d.parent!==this)return this.render(r,s,a);if(d.render(d._ts>0?(G-d._start)*d._ts:(d._dirty?d.totalDuration():d._tDur)+(G-d._start)*d._ts,s,a||Re&&lc(d)),f!==this._time||!this._ts&&!m){M=0,_&&(u+=this._zTime=G?-ie:ie);break}}d=_}}if(M&&!s&&(this.pause(),M.render(f>=o?0:-ie)._zTime=f>=o?1:-1,this._ts))return this._start=S,Na(this),this.render(r,s,a);this._onUpdate&&!s&&Je(this,"onUpdate",!0),(u===l&&this._tTime>=this.totalDuration()||!u&&o)&&(S===this._start||Math.abs(T)!==Math.abs(this._ts))&&(this._lock||((r||!c)&&(u===l&&this._ts>0||!u&&this._ts<0)&&yi(this,1),!s&&!(r<0&&!o)&&(u||o||!l)&&(Je(this,u===l&&r>=0?"onComplete":"onReverseComplete",!0),this._prom&&!(u<l&&this.timeScale()>0)&&this._prom())))}return this},e.add=function(r,s){var a=this;if(Qn(s)||(s=an(this,s,r)),!(r instanceof us)){if(Ue(r))return r.forEach(function(o){return a.add(o,s)}),this;if(be(r))return this.addLabel(r,s);if(fe(r))r=xe.delayedCall(0,r);else return this}return this!==r?bn(this,r,s):this},e.getChildren=function(r,s,a,o){r===void 0&&(r=!0),s===void 0&&(s=!0),a===void 0&&(a=!0),o===void 0&&(o=-un);for(var l=[],c=this._first;c;)c._start>=o&&(c instanceof xe?s&&l.push(c):(a&&l.push(c),r&&l.push.apply(l,c.getChildren(!0,s,a)))),c=c._next;return l},e.getById=function(r){for(var s=this.getChildren(1,1,1),a=s.length;a--;)if(s[a].vars.id===r)return s[a]},e.remove=function(r){return be(r)?this.removeLabel(r):fe(r)?this.killTweensOf(r):(r.parent===this&&Ua(this,r),r===this._recent&&(this._recent=this._last),Yi(this))},e.totalTime=function(r,s){return arguments.length?(this._forcing=1,!this._dp&&this._ts&&(this._start=oe(Ze.time-(this._ts>0?r/this._ts:(this.totalDuration()-r)/-this._ts))),i.prototype.totalTime.call(this,r,s),this._forcing=0,this):this._tTime},e.addLabel=function(r,s){return this.labels[r]=an(this,s),this},e.removeLabel=function(r){return delete this.labels[r],this},e.addPause=function(r,s,a){var o=xe.delayedCall(0,s||os,a);return o.data="isPause",this._hasPause=1,bn(this,o,an(this,r))},e.removePause=function(r){var s=this._first;for(r=an(this,r);s;)s._start===r&&s.data==="isPause"&&yi(s),s=s._next},e.killTweensOf=function(r,s,a){for(var o=this.getTweensOf(r,a),l=o.length;l--;)_i!==o[l]&&o[l].kill(r,s);return this},e.getTweensOf=function(r,s){for(var a=[],o=fn(r),l=this._first,c=Qn(s),u;l;)l instanceof xe?Kd(l._targets,o)&&(c?(!_i||l._initted&&l._ts)&&l.globalTime(0)<=s&&l.globalTime(l.totalDuration())>s:!s||l.isActive())&&a.push(l):(u=l.getTweensOf(o,s)).length&&a.push.apply(a,u),l=l._next;return a},e.tweenTo=function(r,s){s=s||{};var a=this,o=an(a,r),l=s,c=l.startAt,u=l.onStart,h=l.onStartParams,f=l.immediateRender,d,_=xe.to(a,nn({ease:s.ease||"none",lazy:!1,immediateRender:!1,time:o,overwrite:"auto",duration:s.duration||Math.abs((o-(c&&"time"in c?c.time:a._time))/a.timeScale())||ie,onStart:function(){if(a.pause(),!d){var p=s.duration||Math.abs((o-(c&&"time"in c?c.time:a._time))/a.timeScale());_._dur!==p&&Rr(_,p,0,1).render(_._time,!0,!0),d=1}u&&u.apply(_,h||[])}},s));return f?_.render(0):_},e.tweenFromTo=function(r,s,a){return this.tweenTo(s,nn({startAt:{time:an(this,r)}},a))},e.recent=function(){return this._recent},e.nextLabel=function(r){return r===void 0&&(r=this._time),Zc(this,an(this,r))},e.previousLabel=function(r){return r===void 0&&(r=this._time),Zc(this,an(this,r),1)},e.currentLabel=function(r){return arguments.length?this.seek(r,!0):this.previousLabel(this._time+ie)},e.shiftChildren=function(r,s,a){a===void 0&&(a=0);var o=this._first,l=this.labels,c;for(r=oe(r);o;)o._start>=a&&(o._start+=r,o._end+=r),o=o._next;if(s)for(c in l)l[c]>=a&&(l[c]+=r);return Yi(this)},e.invalidate=function(r){var s=this._first;for(this._lock=0;s;)s.invalidate(r),s=s._next;return i.prototype.invalidate.call(this,r)},e.clear=function(r){r===void 0&&(r=!0);for(var s=this._first,a;s;)a=s._next,this.remove(s),s=a;return this._dp&&(this._time=this._tTime=this._pTime=0),r&&(this.labels={}),Yi(this)},e.totalDuration=function(r){var s=0,a=this,o=a._last,l=un,c,u,h;if(arguments.length)return a.timeScale((a._repeat<0?a.duration():a.totalDuration())/(a.reversed()?-r:r));if(a._dirty){for(h=a.parent;o;)c=o._prev,o._dirty&&o.totalDuration(),u=o._start,u>l&&a._sort&&o._ts&&!a._lock?(a._lock=1,bn(a,o,u-o._delay,1)._lock=0):l=u,u<0&&o._ts&&(s-=u,(!h&&!a._dp||h&&h.smoothChildTiming)&&(a._start+=oe(u/a._ts),a._time-=u,a._tTime-=u),a.shiftChildren(-u,!1,-1/0),l=0),o._end>s&&o._ts&&(s=o._end),o=c;Rr(a,a===le&&a._time>s?a._time:s,1,1),a._dirty=0}return a._tDur},t.updateRoot=function(r){if(le._ts&&(Of(le,va(r,le)),Nf=Ze.frame),Ze.frame>=qc){qc+=Qe.autoSleep||120;var s=le._first;if((!s||!s._ts)&&Qe.autoSleep&&Ze._listeners.length<2){for(;s&&!s._ts;)s=s._next;s||Ze.sleep()}}},t}(us);nn(Fe.prototype,{_lock:0,_hasPause:0,_forcing:0});var xp=function(t,e,n,r,s,a,o){var l=new Ge(this._pt,t,e,0,1,fh,null,s),c=0,u=0,h,f,d,_,g,p,m,M;for(l.b=n,l.e=r,n+="",r+="",(m=~r.indexOf("random("))&&(r=ls(r)),a&&(M=[n,r],a(M,t,e),n=M[0],r=M[1]),f=n.match(qa)||[];h=qa.exec(r);)_=h[0],g=r.substring(c,h.index),d?d=(d+1)%5:g.substr(-5)==="rgba("&&(d=1),_!==f[u++]&&(p=parseFloat(f[u-1])||0,l._pt={_next:l._pt,p:g||u===1?g:",",s:p,c:_.charAt(1)==="="?vr(p,_)-p:parseFloat(_)-p,m:d&&d<4?Math.round:0},c=qa.lastIndex);return l.c=c<r.length?r.substring(c,r.length):"",l.fp=o,(Df.test(r)||m)&&(l.e=0),this._pt=l,l},cc=function(t,e,n,r,s,a,o,l,c,u){fe(r)&&(r=r(s||0,t,a));var h=t[e],f=n!=="get"?n:fe(h)?c?t[e.indexOf("set")||!fe(t["get"+e.substr(3)])?e:"get"+e.substr(3)](c):t[e]():h,d=fe(h)?c?Ep:ch:fc,_;if(be(r)&&(~r.indexOf("random(")&&(r=ls(r)),r.charAt(1)==="="&&(_=vr(f,r)+(Le(f)||0),(_||_===0)&&(r=_))),!u||f!==r||qo)return!isNaN(f*r)&&r!==""?(_=new Ge(this._pt,t,e,+f||0,r-(f||0),typeof h=="boolean"?bp:uh,0,d),c&&(_.fp=c),o&&_.modifier(o,this,t),this._pt=_):(!h&&!(e in t)&&rc(e,r),xp.call(this,t,e,f,r,d,l||Qe.stringFilter,c))},vp=function(t,e,n,r,s){if(fe(t)&&(t=ss(t,s,e,n,r)),!In(t)||t.style&&t.nodeType||Ue(t)||Cf(t))return be(t)?ss(t,s,e,n,r):t;var a={},o;for(o in t)a[o]=ss(t[o],s,e,n,r);return a},ah=function(t,e,n,r,s,a){var o,l,c,u;if(Ke[t]&&(o=new Ke[t]).init(s,o.rawVars?e[t]:vp(e[t],r,s,a,n),n,r,a)!==!1&&(n._pt=l=new Ge(n._pt,s,t,0,1,o.render,o,0,o.priority),n!==xr))for(c=n._ptLookup[n._targets.indexOf(s)],u=o._props.length;u--;)c[o._props[u]]=l;return o},_i,qo,uc=function i(t,e,n){var r=t.vars,s=r.ease,a=r.startAt,o=r.immediateRender,l=r.lazy,c=r.onUpdate,u=r.runBackwards,h=r.yoyoEase,f=r.keyframes,d=r.autoRevert,_=t._dur,g=t._startAt,p=t._targets,m=t.parent,M=m&&m.data==="nested"?m.vars.targets:p,T=t._overwrite==="auto"&&!tc,S=t.timeline,b,A,R,x,y,G,D,B,k,X,C,L,P;if(S&&(!f||!s)&&(s="none"),t._ease=$i(s,br.ease),t._yEase=h?nh($i(h===!0?s:h,br.ease)):0,h&&t._yoyo&&!t._repeat&&(h=t._yEase,t._yEase=t._ease,t._ease=h),t._from=!S&&!!r.runBackwards,!S||f&&!r.stagger){if(B=p[0]?qi(p[0]).harness:0,L=B&&r[B.prop],b=xa(r,sc),g&&(g._zTime<0&&g.progress(1),e<0&&u&&o&&!d?g.render(-1,!0):g.revert(u&&_?ra:Yd),g._lazy=0),a){if(yi(t._startAt=xe.set(p,nn({data:"isStart",overwrite:!1,parent:m,immediateRender:!0,lazy:!g&&ze(l),startAt:null,delay:0,onUpdate:c&&function(){return Je(t,"onUpdate")},stagger:0},a))),t._startAt._dp=0,t._startAt._sat=t,e<0&&(Re||!o&&!d)&&t._startAt.revert(ra),o&&_&&e<=0&&n<=0){e&&(t._zTime=e);return}}else if(u&&_&&!g){if(e&&(o=!1),R=nn({overwrite:!1,data:"isFromStart",lazy:o&&!g&&ze(l),immediateRender:o,stagger:0,parent:m},b),L&&(R[B.prop]=L),yi(t._startAt=xe.set(p,R)),t._startAt._dp=0,t._startAt._sat=t,e<0&&(Re?t._startAt.revert(ra):t._startAt.render(-1,!0)),t._zTime=e,!o)i(t._startAt,ie,ie);else if(!e)return}for(t._pt=t._ptCache=0,l=_&&ze(l)||l&&!_,A=0;A<p.length;A++){if(y=p[A],D=y._gsap||oc(p)[A]._gsap,t._ptLookup[A]=X={},zo[D.id]&&Mi.length&&ga(),C=M===p?A:M.indexOf(y),B&&(k=new B).init(y,L||b,t,C,M)!==!1&&(t._pt=x=new Ge(t._pt,y,k.name,0,1,k.render,k,0,k.priority),k._props.forEach(function(z){X[z]=x}),k.priority&&(G=1)),!B||L)for(R in b)Ke[R]&&(k=ah(R,b,t,C,y,M))?k.priority&&(G=1):X[R]=x=cc.call(t,y,R,"get",b[R],C,M,0,r.stringFilter);t._op&&t._op[A]&&t.kill(y,t._op[A]),T&&t._pt&&(_i=t,le.killTweensOf(y,X,t.globalTime(e)),P=!t.parent,_i=0),t._pt&&l&&(zo[D.id]=1)}G&&hh(t),t._onInit&&t._onInit(t)}t._onUpdate=c,t._initted=(!t._op||t._pt)&&!P,f&&e<=0&&S.render(un,!0,!0)},Mp=function(t,e,n,r,s,a,o,l){var c=(t._pt&&t._ptCache||(t._ptCache={}))[e],u,h,f,d;if(!c)for(c=t._ptCache[e]=[],f=t._ptLookup,d=t._targets.length;d--;){if(u=f[d][e],u&&u.d&&u.d._pt)for(u=u.d._pt;u&&u.p!==e&&u.fp!==e;)u=u._next;if(!u)return qo=1,t.vars[e]="+=0",uc(t,o),qo=0,l?as(e+" not eligible for reset"):1;c.push(u)}for(d=c.length;d--;)h=c[d],u=h._pt||h,u.s=(r||r===0)&&!s?r:u.s+(r||0)+a*u.c,u.c=n-u.s,h.e&&(h.e=pe(n)+Le(h.e)),h.b&&(h.b=u.s+Le(h.b))},Sp=function(t,e){var n=t[0]?qi(t[0]).harness:0,r=n&&n.aliases,s,a,o,l;if(!r)return e;s=Ar({},e);for(a in r)if(a in s)for(l=r[a].split(","),o=l.length;o--;)s[l[o]]=s[a];return s},yp=function(t,e,n,r){var s=e.ease||r||"power1.inOut",a,o;if(Ue(e))o=n[t]||(n[t]=[]),e.forEach(function(l,c){return o.push({t:c/(e.length-1)*100,v:l,e:s})});else for(a in e)o=n[a]||(n[a]=[]),a==="ease"||o.push({t:parseFloat(t),v:e[a],e:s})},ss=function(t,e,n,r,s){return fe(t)?t.call(e,n,r,s):be(t)&&~t.indexOf("random(")?ls(t):t},oh=ac+"repeat,repeatDelay,yoyo,repeatRefresh,yoyoEase,autoRevert",lh={};Ve(oh+",id,stagger,delay,duration,paused,scrollTrigger",function(i){return lh[i]=1});var xe=function(i){wf(t,i);function t(n,r,s,a){var o;typeof r=="number"&&(s.duration=r,r=s,s=null),o=i.call(this,a?r:is(r))||this;var l=o.vars,c=l.duration,u=l.delay,h=l.immediateRender,f=l.stagger,d=l.overwrite,_=l.keyframes,g=l.defaults,p=l.scrollTrigger,m=l.yoyoEase,M=r.parent||le,T=(Ue(n)||Cf(n)?Qn(n[0]):"length"in r)?[n]:fn(n),S,b,A,R,x,y,G,D;if(o._targets=T.length?oc(T):as("GSAP target "+n+" not found. https://gsap.com",!Qe.nullTargetWarn)||[],o._ptLookup=[],o._overwrite=d,_||f||Ps(c)||Ps(u)){if(r=o.vars,S=o.timeline=new Fe({data:"nested",defaults:g||{},targets:M&&M.data==="nested"?M.vars.targets:T}),S.kill(),S.parent=S._dp=qn(o),S._start=0,f||Ps(c)||Ps(u)){if(R=T.length,G=f&&qf(f),In(f))for(x in f)~oh.indexOf(x)&&(D||(D={}),D[x]=f[x]);for(b=0;b<R;b++)A=xa(r,lh),A.stagger=0,m&&(A.yoyoEase=m),D&&Ar(A,D),y=T[b],A.duration=+ss(c,qn(o),b,y,T),A.delay=(+ss(u,qn(o),b,y,T)||0)-o._delay,!f&&R===1&&A.delay&&(o._delay=u=A.delay,o._start+=u,A.delay=0),S.to(y,A,G?G(b,y,T):0),S._ease=Vt.none;S.duration()?c=u=0:o.timeline=0}else if(_){is(nn(S.vars.defaults,{ease:"none"})),S._ease=$i(_.ease||r.ease||"none");var B=0,k,X,C;if(Ue(_))_.forEach(function(L){return S.to(T,L,">")}),S.duration();else{A={};for(x in _)x==="ease"||x==="easeEach"||yp(x,_[x],A,_.easeEach);for(x in A)for(k=A[x].sort(function(L,P){return L.t-P.t}),B=0,b=0;b<k.length;b++)X=k[b],C={ease:X.e,duration:(X.t-(b?k[b-1].t:0))/100*c},C[x]=X.v,S.to(T,C,B),B+=C.duration;S.duration()<c&&S.to({},{duration:c-S.duration()})}}c||o.duration(c=S.duration())}else o.timeline=0;return d===!0&&!tc&&(_i=qn(o),le.killTweensOf(T),_i=0),bn(M,qn(o),s),r.reversed&&o.reverse(),r.paused&&o.paused(!0),(h||!c&&!_&&o._start===oe(M._time)&&ze(h)&&Qd(qn(o))&&M.data!=="nested")&&(o._tTime=-ie,o.render(Math.max(0,-u)||0)),p&&Gf(qn(o),p),o}var e=t.prototype;return e.render=function(r,s,a){var o=this._time,l=this._tDur,c=this._dur,u=r<0,h=r>l-ie&&!u?l:r<ie?0:r,f,d,_,g,p,m,M,T,S;if(!c)ep(this,r,s,a);else if(h!==this._tTime||!r||a||!this._initted&&this._tTime||this._startAt&&this._zTime<0!==u||this._lazy){if(f=h,T=this.timeline,this._repeat){if(g=c+this._rDelay,this._repeat<-1&&u)return this.totalTime(g*100+r,s,a);if(f=oe(h%g),h===l?(_=this._repeat,f=c):(p=oe(h/g),_=~~p,_&&_===p?(f=c,_--):f>c&&(f=c)),m=this._yoyo&&_&1,m&&(S=this._yEase,f=c-f),p=wr(this._tTime,g),f===o&&!a&&this._initted&&_===p)return this._tTime=h,this;_!==p&&(T&&this._yEase&&ih(T,m),this.vars.repeatRefresh&&!m&&!this._lock&&f!==g&&this._initted&&(this._lock=a=1,this.render(oe(g*_),!0).invalidate()._lock=0))}if(!this._initted){if(Hf(this,u?r:f,a,s,h))return this._tTime=0,this;if(o!==this._time&&!(a&&this.vars.repeatRefresh&&_!==p))return this;if(c!==this._dur)return this.render(r,s,a)}if(this._tTime=h,this._time=f,!this._act&&this._ts&&(this._act=1,this._lazy=0),this.ratio=M=(S||this._ease)(f/c),this._from&&(this.ratio=M=1-M),!o&&h&&!s&&!p&&(Je(this,"onStart"),this._tTime!==h))return this;for(d=this._pt;d;)d.r(M,d.d),d=d._next;T&&T.render(r<0?r:T._dur*T._ease(f/this._dur),s,a)||this._startAt&&(this._zTime=r),this._onUpdate&&!s&&(u&&Vo(this,r,s,a),Je(this,"onUpdate")),this._repeat&&_!==p&&this.vars.onRepeat&&!s&&this.parent&&Je(this,"onRepeat"),(h===this._tDur||!h)&&this._tTime===h&&(u&&!this._onUpdate&&Vo(this,r,!0,!0),(r||!c)&&(h===this._tDur&&this._ts>0||!h&&this._ts<0)&&yi(this,1),!s&&!(u&&!o)&&(h||o||m)&&(Je(this,h===l?"onComplete":"onReverseComplete",!0),this._prom&&!(h<l&&this.timeScale()>0)&&this._prom()))}return this},e.targets=function(){return this._targets},e.invalidate=function(r){return(!r||!this.vars.runBackwards)&&(this._startAt=0),this._pt=this._op=this._onUpdate=this._lazy=this.ratio=0,this._ptLookup=[],this.timeline&&this.timeline.invalidate(r),i.prototype.invalidate.call(this,r)},e.resetTo=function(r,s,a,o,l){cs||Ze.wake(),this._ts||this.play();var c=Math.min(this._dur,(this._dp._time-this._start)*this._ts),u;return this._initted||uc(this,c),u=this._ease(c/this._dur),Mp(this,r,s,a,o,u,c,l)?this.resetTo(r,s,a,o,1):(Fa(this,0),this.parent||zf(this._dp,this,"_first","_last",this._dp._sort?"_start":0),this.render(0))},e.kill=function(r,s){if(s===void 0&&(s="all"),!r&&(!s||s==="all"))return this._lazy=this._pt=0,this.parent?Zr(this):this.scrollTrigger&&this.scrollTrigger.kill(!!Re),this;if(this.timeline){var a=this.timeline.totalDuration();return this.timeline.killTweensOf(r,s,_i&&_i.vars.overwrite!==!0)._first||Zr(this),this.parent&&a!==this.timeline.totalDuration()&&Rr(this,this._dur*this.timeline._tDur/a,0,1),this}var o=this._targets,l=r?fn(r):o,c=this._ptLookup,u=this._pt,h,f,d,_,g,p,m;if((!s||s==="all")&&Jd(o,l))return s==="all"&&(this._pt=0),Zr(this);for(h=this._op=this._op||[],s!=="all"&&(be(s)&&(g={},Ve(s,function(M){return g[M]=1}),s=g),s=Sp(o,s)),m=o.length;m--;)if(~l.indexOf(o[m])){f=c[m],s==="all"?(h[m]=s,_=f,d={}):(d=h[m]=h[m]||{},_=s);for(g in _)p=f&&f[g],p&&((!("kill"in p.d)||p.d.kill(g)===!0)&&Ua(this,p,"_pt"),delete f[g]),d!=="all"&&(d[g]=1)}return this._initted&&!this._pt&&u&&Zr(this),this},t.to=function(r,s){return new t(r,s,arguments[2])},t.from=function(r,s){return rs(1,arguments)},t.delayedCall=function(r,s,a,o){return new t(s,0,{immediateRender:!1,lazy:!1,overwrite:!1,delay:r,onComplete:s,onReverseComplete:s,onCompleteParams:a,onReverseCompleteParams:a,callbackScope:o})},t.fromTo=function(r,s,a){return rs(2,arguments)},t.set=function(r,s){return s.duration=0,s.repeatDelay||(s.repeat=0),new t(r,s)},t.killTweensOf=function(r,s,a){return le.killTweensOf(r,s,a)},t}(us);nn(xe.prototype,{_targets:[],_lazy:0,_startAt:0,_op:0,_onInit:0});Ve("staggerTo,staggerFrom,staggerFromTo",function(i){xe[i]=function(){var t=new Fe,e=Ho.call(arguments,0);return e.splice(i==="staggerFromTo"?5:4,0,0),t[i].apply(t,e)}});var fc=function(t,e,n){return t[e]=n},ch=function(t,e,n){return t[e](n)},Ep=function(t,e,n,r){return t[e](r.fp,n)},Tp=function(t,e,n){return t.setAttribute(e,n)},hc=function(t,e){return fe(t[e])?ch:ec(t[e])&&t.setAttribute?Tp:fc},uh=function(t,e){return e.set(e.t,e.p,Math.round((e.s+e.c*t)*1e6)/1e6,e)},bp=function(t,e){return e.set(e.t,e.p,!!(e.s+e.c*t),e)},fh=function(t,e){var n=e._pt,r="";if(!t&&e.b)r=e.b;else if(t===1&&e.e)r=e.e;else{for(;n;)r=n.p+(n.m?n.m(n.s+n.c*t):Math.round((n.s+n.c*t)*1e4)/1e4)+r,n=n._next;r+=e.c}e.set(e.t,e.p,r,e)},dc=function(t,e){for(var n=e._pt;n;)n.r(t,n.d),n=n._next},Ap=function(t,e,n,r){for(var s=this._pt,a;s;)a=s._next,s.p===r&&s.modifier(t,e,n),s=a},wp=function(t){for(var e=this._pt,n,r;e;)r=e._next,e.p===t&&!e.op||e.op===t?Ua(this,e,"_pt"):e.dep||(n=1),e=r;return!n},Rp=function(t,e,n,r){r.mSet(t,e,r.m.call(r.tween,n,r.mt),r)},hh=function(t){for(var e=t._pt,n,r,s,a;e;){for(n=e._next,r=s;r&&r.pr>e.pr;)r=r._next;(e._prev=r?r._prev:a)?e._prev._next=e:s=e,(e._next=r)?r._prev=e:a=e,e=n}t._pt=s},Ge=function(){function i(e,n,r,s,a,o,l,c,u){this.t=n,this.s=s,this.c=a,this.p=r,this.r=o||uh,this.d=l||this,this.set=c||fc,this.pr=u||0,this._next=e,e&&(e._prev=this)}var t=i.prototype;return t.modifier=function(n,r,s){this.mSet=this.mSet||this.set,this.set=Rp,this.m=n,this.mt=s,this.tween=r},i}();Ve(ac+"parent,duration,ease,delay,overwrite,runBackwards,startAt,yoyo,immediateRender,repeat,repeatDelay,data,paused,reversed,lazy,callbackScope,stringFilter,id,yoyoEase,stagger,inherit,repeatRefresh,keyframes,autoRevert,scrollTrigger",function(i){return sc[i]=1});en.TweenMax=en.TweenLite=xe;en.TimelineLite=en.TimelineMax=Fe;le=new Fe({sortChildren:!1,defaults:br,autoRemoveChildren:!0,id:"root",smoothChildTiming:!0});Qe.stringFilter=eh;var Ki=[],aa={},Cp=[],jc=0,Pp=0,Ja=function(t){return(aa[t]||Cp).map(function(e){return e()})},Yo=function(){var t=Date.now(),e=[];t-jc>2&&(Ja("matchMediaInit"),Ki.forEach(function(n){var r=n.queries,s=n.conditions,a,o,l,c;for(o in r)a=En.matchMedia(r[o]).matches,a&&(l=1),a!==s[o]&&(s[o]=a,c=1);c&&(n.revert(),l&&e.push(n))}),Ja("matchMediaRevert"),e.forEach(function(n){return n.onMatch(n,function(r){return n.add(null,r)})}),jc=t,Ja("matchMedia"))},dh=function(){function i(e,n){this.selector=n&&Wo(n),this.data=[],this._r=[],this.isReverted=!1,this.id=Pp++,e&&this.add(e)}var t=i.prototype;return t.add=function(n,r,s){fe(n)&&(s=r,r=n,n=fe);var a=this,o=function(){var c=ae,u=a.selector,h;return c&&c!==a&&c.data.push(a),s&&(a.selector=Wo(s)),ae=a,h=r.apply(a,arguments),fe(h)&&a._r.push(h),ae=c,a.selector=u,a.isReverted=!1,h};return a.last=o,n===fe?o(a,function(l){return a.add(null,l)}):n?a[n]=o:o},t.ignore=function(n){var r=ae;ae=null,n(this),ae=r},t.getTweens=function(){var n=[];return this.data.forEach(function(r){return r instanceof i?n.push.apply(n,r.getTweens()):r instanceof xe&&!(r.parent&&r.parent.data==="nested")&&n.push(r)}),n},t.clear=function(){this._r.length=this.data.length=0},t.kill=function(n,r){var s=this;if(n?function(){for(var o=s.getTweens(),l=s.data.length,c;l--;)c=s.data[l],c.data==="isFlip"&&(c.revert(),c.getChildren(!0,!0,!1).forEach(function(u){return o.splice(o.indexOf(u),1)}));for(o.map(function(u){return{g:u._dur||u._delay||u._sat&&!u._sat.vars.immediateRender?u.globalTime(0):-1/0,t:u}}).sort(function(u,h){return h.g-u.g||-1/0}).forEach(function(u){return u.t.revert(n)}),l=s.data.length;l--;)c=s.data[l],c instanceof Fe?c.data!=="nested"&&(c.scrollTrigger&&c.scrollTrigger.revert(),c.kill()):!(c instanceof xe)&&c.revert&&c.revert(n);s._r.forEach(function(u){return u(n,s)}),s.isReverted=!0}():this.data.forEach(function(o){return o.kill&&o.kill()}),this.clear(),r)for(var a=Ki.length;a--;)Ki[a].id===this.id&&Ki.splice(a,1)},t.revert=function(n){this.kill(n||{})},i}(),Dp=function(){function i(e){this.contexts=[],this.scope=e,ae&&ae.data.push(this)}var t=i.prototype;return t.add=function(n,r,s){In(n)||(n={matches:n});var a=new dh(0,s||this.scope),o=a.conditions={},l,c,u;ae&&!a.selector&&(a.selector=ae.selector),this.contexts.push(a),r=a.add("onMatch",r),a.queries=n;for(c in n)c==="all"?u=1:(l=En.matchMedia(n[c]),l&&(Ki.indexOf(a)<0&&Ki.push(a),(o[c]=l.matches)&&(u=1),l.addListener?l.addListener(Yo):l.addEventListener("change",Yo)));return u&&r(a,function(h){return a.add(null,h)}),this},t.revert=function(n){this.kill(n||{})},t.kill=function(n){this.contexts.forEach(function(r){return r.kill(n,!0)})},i}(),Ma={registerPlugin:function(){for(var t=arguments.length,e=new Array(t),n=0;n<t;n++)e[n]=arguments[n];e.forEach(function(r){return jf(r)})},timeline:function(t){return new Fe(t)},getTweensOf:function(t,e){return le.getTweensOf(t,e)},getProperty:function(t,e,n,r){be(t)&&(t=fn(t)[0]);var s=qi(t||{}).get,a=n?kf:Bf;return n==="native"&&(n=""),t&&(e?a((Ke[e]&&Ke[e].get||s)(t,e,n,r)):function(o,l,c){return a((Ke[o]&&Ke[o].get||s)(t,o,l,c))})},quickSetter:function(t,e,n){if(t=fn(t),t.length>1){var r=t.map(function(u){return Xe.quickSetter(u,e,n)}),s=r.length;return function(u){for(var h=s;h--;)r[h](u)}}t=t[0]||{};var a=Ke[e],o=qi(t),l=o.harness&&(o.harness.aliases||{})[e]||e,c=a?function(u){var h=new a;xr._pt=0,h.init(t,n?u+n:u,xr,0,[t]),h.render(1,h),xr._pt&&dc(1,xr)}:o.set(t,l);return a?c:function(u){return c(t,l,n?u+n:u,o,1)}},quickTo:function(t,e,n){var r,s=Xe.to(t,nn((r={},r[e]="+=0.1",r.paused=!0,r.stagger=0,r),n||{})),a=function(l,c,u){return s.resetTo(e,l,c,u)};return a.tween=s,a},isTweening:function(t){return le.getTweensOf(t,!0).length>0},defaults:function(t){return t&&t.ease&&(t.ease=$i(t.ease,br.ease)),Yc(br,t||{})},config:function(t){return Yc(Qe,t||{})},registerEffect:function(t){var e=t.name,n=t.effect,r=t.plugins,s=t.defaults,a=t.extendTimeline;(r||"").split(",").forEach(function(o){return o&&!Ke[o]&&!en[o]&&as(e+" effect requires "+o+" plugin.")}),Ya[e]=function(o,l,c){return n(fn(o),nn(l||{},s),c)},a&&(Fe.prototype[e]=function(o,l,c){return this.add(Ya[e](o,In(l)?l:(c=l)&&{},this),c)})},registerEase:function(t,e){Vt[t]=$i(e)},parseEase:function(t,e){return arguments.length?$i(t,e):Vt},getById:function(t){return le.getById(t)},exportRoot:function(t,e){t===void 0&&(t={});var n=new Fe(t),r,s;for(n.smoothChildTiming=ze(t.smoothChildTiming),le.remove(n),n._dp=0,n._time=n._tTime=le._time,r=le._first;r;)s=r._next,(e||!(!r._dur&&r instanceof xe&&r.vars.onComplete===r._targets[0]))&&bn(n,r,r._start-r._delay),r=s;return bn(le,n,0),n},context:function(t,e){return t?new dh(t,e):ae},matchMedia:function(t){return new Dp(t)},matchMediaRefresh:function(){return Ki.forEach(function(t){var e=t.conditions,n,r;for(r in e)e[r]&&(e[r]=!1,n=1);n&&t.revert()})||Yo()},addEventListener:function(t,e){var n=aa[t]||(aa[t]=[]);~n.indexOf(e)||n.push(e)},removeEventListener:function(t,e){var n=aa[t],r=n&&n.indexOf(e);r>=0&&n.splice(r,1)},utils:{wrap:cp,wrapYoyo:up,distribute:qf,random:$f,snap:Yf,normalize:lp,getUnit:Le,clamp:rp,splitColor:Qf,toArray:fn,selector:Wo,mapRange:Zf,pipe:ap,unitize:op,interpolate:fp,shuffle:Xf},install:If,effects:Ya,ticker:Ze,updateRoot:Fe.updateRoot,plugins:Ke,globalTimeline:le,core:{PropTween:Ge,globals:Uf,Tween:xe,Timeline:Fe,Animation:us,getCache:qi,_removeLinkedListItem:Ua,reverting:function(){return Re},context:function(t){return t&&ae&&(ae.data.push(t),t._ctx=ae),ae},suppressOverwrites:function(t){return tc=t}}};Ve("to,from,fromTo,delayedCall,set,killTweensOf",function(i){return Ma[i]=xe[i]});Ze.add(Fe.updateRoot);xr=Ma.to({},{duration:0});var Lp=function(t,e){for(var n=t._pt;n&&n.p!==e&&n.op!==e&&n.fp!==e;)n=n._next;return n},Ip=function(t,e){var n=t._targets,r,s,a;for(r in e)for(s=n.length;s--;)a=t._ptLookup[s][r],a&&(a=a.d)&&(a._pt&&(a=Lp(a,r)),a&&a.modifier&&a.modifier(e[r],t,n[s],r))},ja=function(t,e){return{name:t,headless:1,rawVars:1,init:function(r,s,a){a._onInit=function(o){var l,c;if(be(s)&&(l={},Ve(s,function(u){return l[u]=1}),s=l),e){l={};for(c in s)l[c]=e(s[c]);s=l}Ip(o,s)}}}},Xe=Ma.registerPlugin({name:"attr",init:function(t,e,n,r,s){var a,o,l;this.tween=n;for(a in e)l=t.getAttribute(a)||"",o=this.add(t,"setAttribute",(l||0)+"",e[a],r,s,0,0,a),o.op=a,o.b=l,this._props.push(a)},render:function(t,e){for(var n=e._pt;n;)Re?n.set(n.t,n.p,n.b,n):n.r(t,n.d),n=n._next}},{name:"endArray",headless:1,init:function(t,e){for(var n=e.length;n--;)this.add(t,n,t[n]||0,e[n],0,0,0,0,0,1)}},ja("roundProps",Xo),ja("modifiers"),ja("snap",Yf))||Ma;xe.version=Fe.version=Xe.version="3.14.2";Lf=1;nc()&&Cr();Vt.Power0;Vt.Power1;Vt.Power2;Vt.Power3;Vt.Power4;Vt.Linear;Vt.Quad;Vt.Cubic;Vt.Quart;Vt.Quint;Vt.Strong;Vt.Elastic;Vt.Back;Vt.SteppedEase;Vt.Bounce;Vt.Sine;Vt.Expo;Vt.Circ;/*!
 * CSSPlugin 3.14.2
 * https://gsap.com
 *
 * Copyright 2008-2025, GreenSock. All rights reserved.
 * Subject to the terms at https://gsap.com/standard-license
 * @author: Jack Doyle, jack@greensock.com
*/var Qc,gi,Mr,pc,Gi,tu,mc,Up=function(){return typeof window<"u"},ti={},Oi=180/Math.PI,Sr=Math.PI/180,nr=Math.atan2,eu=1e8,_c=/([A-Z])/g,Np=/(left|right|width|margin|padding|x)/i,Fp=/[\s,\(]\S/,An={autoAlpha:"opacity,visibility",scale:"scaleX,scaleY",alpha:"opacity"},$o=function(t,e){return e.set(e.t,e.p,Math.round((e.s+e.c*t)*1e4)/1e4+e.u,e)},Op=function(t,e){return e.set(e.t,e.p,t===1?e.e:Math.round((e.s+e.c*t)*1e4)/1e4+e.u,e)},Bp=function(t,e){return e.set(e.t,e.p,t?Math.round((e.s+e.c*t)*1e4)/1e4+e.u:e.b,e)},kp=function(t,e){return e.set(e.t,e.p,t===1?e.e:t?Math.round((e.s+e.c*t)*1e4)/1e4+e.u:e.b,e)},zp=function(t,e){var n=e.s+e.c*t;e.set(e.t,e.p,~~(n+(n<0?-.5:.5))+e.u,e)},ph=function(t,e){return e.set(e.t,e.p,t?e.e:e.b,e)},mh=function(t,e){return e.set(e.t,e.p,t!==1?e.b:e.e,e)},Vp=function(t,e,n){return t.style[e]=n},Gp=function(t,e,n){return t.style.setProperty(e,n)},Hp=function(t,e,n){return t._gsap[e]=n},Wp=function(t,e,n){return t._gsap.scaleX=t._gsap.scaleY=n},Xp=function(t,e,n,r,s){var a=t._gsap;a.scaleX=a.scaleY=n,a.renderTransform(s,a)},qp=function(t,e,n,r,s){var a=t._gsap;a[e]=n,a.renderTransform(s,a)},ce="transform",He=ce+"Origin",Yp=function i(t,e){var n=this,r=this.target,s=r.style,a=r._gsap;if(t in ti&&s){if(this.tfm=this.tfm||{},t!=="transform")t=An[t]||t,~t.indexOf(",")?t.split(",").forEach(function(o){return n.tfm[o]=Yn(r,o)}):this.tfm[t]=a.x?a[t]:Yn(r,t),t===He&&(this.tfm.zOrigin=a.zOrigin);else return An.transform.split(",").forEach(function(o){return i.call(n,o,e)});if(this.props.indexOf(ce)>=0)return;a.svg&&(this.svgo=r.getAttribute("data-svg-origin"),this.props.push(He,e,"")),t=ce}(s||e)&&this.props.push(t,e,s[t])},_h=function(t){t.translate&&(t.removeProperty("translate"),t.removeProperty("scale"),t.removeProperty("rotate"))},$p=function(){var t=this.props,e=this.target,n=e.style,r=e._gsap,s,a;for(s=0;s<t.length;s+=3)t[s+1]?t[s+1]===2?e[t[s]](t[s+2]):e[t[s]]=t[s+2]:t[s+2]?n[t[s]]=t[s+2]:n.removeProperty(t[s].substr(0,2)==="--"?t[s]:t[s].replace(_c,"-$1").toLowerCase());if(this.tfm){for(a in this.tfm)r[a]=this.tfm[a];r.svg&&(r.renderTransform(),e.setAttribute("data-svg-origin",this.svgo||"")),s=mc(),(!s||!s.isStart)&&!n[ce]&&(_h(n),r.zOrigin&&n[He]&&(n[He]+=" "+r.zOrigin+"px",r.zOrigin=0,r.renderTransform()),r.uncache=1)}},gh=function(t,e){var n={target:t,props:[],revert:$p,save:Yp};return t._gsap||Xe.core.getCache(t),e&&t.style&&t.nodeType&&e.split(",").forEach(function(r){return n.save(r)}),n},xh,Ko=function(t,e){var n=gi.createElementNS?gi.createElementNS((e||"http://www.w3.org/1999/xhtml").replace(/^https/,"http"),t):gi.createElement(t);return n&&n.style?n:gi.createElement(t)},je=function i(t,e,n){var r=getComputedStyle(t);return r[e]||r.getPropertyValue(e.replace(_c,"-$1").toLowerCase())||r.getPropertyValue(e)||!n&&i(t,Pr(e)||e,1)||""},nu="O,Moz,ms,Ms,Webkit".split(","),Pr=function(t,e,n){var r=e||Gi,s=r.style,a=5;if(t in s&&!n)return t;for(t=t.charAt(0).toUpperCase()+t.substr(1);a--&&!(nu[a]+t in s););return a<0?null:(a===3?"ms":a>=0?nu[a]:"")+t},Zo=function(){Up()&&window.document&&(Qc=window,gi=Qc.document,Mr=gi.documentElement,Gi=Ko("div")||{style:{}},Ko("div"),ce=Pr(ce),He=ce+"Origin",Gi.style.cssText="border-width:0;line-height:0;position:absolute;padding:0",xh=!!Pr("perspective"),mc=Xe.core.reverting,pc=1)},iu=function(t){var e=t.ownerSVGElement,n=Ko("svg",e&&e.getAttribute("xmlns")||"http://www.w3.org/2000/svg"),r=t.cloneNode(!0),s;r.style.display="block",n.appendChild(r),Mr.appendChild(n);try{s=r.getBBox()}catch{}return n.removeChild(r),Mr.removeChild(n),s},ru=function(t,e){for(var n=e.length;n--;)if(t.hasAttribute(e[n]))return t.getAttribute(e[n])},vh=function(t){var e,n;try{e=t.getBBox()}catch{e=iu(t),n=1}return e&&(e.width||e.height)||n||(e=iu(t)),e&&!e.width&&!e.x&&!e.y?{x:+ru(t,["x","cx","x1"])||0,y:+ru(t,["y","cy","y1"])||0,width:0,height:0}:e},Mh=function(t){return!!(t.getCTM&&(!t.parentNode||t.ownerSVGElement)&&vh(t))},Ei=function(t,e){if(e){var n=t.style,r;e in ti&&e!==He&&(e=ce),n.removeProperty?(r=e.substr(0,2),(r==="ms"||e.substr(0,6)==="webkit")&&(e="-"+e),n.removeProperty(r==="--"?e:e.replace(_c,"-$1").toLowerCase())):n.removeAttribute(e)}},xi=function(t,e,n,r,s,a){var o=new Ge(t._pt,e,n,0,1,a?mh:ph);return t._pt=o,o.b=r,o.e=s,t._props.push(n),o},su={deg:1,rad:1,turn:1},Kp={grid:1,flex:1},Ti=function i(t,e,n,r){var s=parseFloat(n)||0,a=(n+"").trim().substr((s+"").length)||"px",o=Gi.style,l=Np.test(e),c=t.tagName.toLowerCase()==="svg",u=(c?"client":"offset")+(l?"Width":"Height"),h=100,f=r==="px",d=r==="%",_,g,p,m;if(r===a||!s||su[r]||su[a])return s;if(a!=="px"&&!f&&(s=i(t,e,n,"px")),m=t.getCTM&&Mh(t),(d||a==="%")&&(ti[e]||~e.indexOf("adius")))return _=m?t.getBBox()[l?"width":"height"]:t[u],pe(d?s/_*h:s/100*_);if(o[l?"width":"height"]=h+(f?a:r),g=r!=="rem"&&~e.indexOf("adius")||r==="em"&&t.appendChild&&!c?t:t.parentNode,m&&(g=(t.ownerSVGElement||{}).parentNode),(!g||g===gi||!g.appendChild)&&(g=gi.body),p=g._gsap,p&&d&&p.width&&l&&p.time===Ze.time&&!p.uncache)return pe(s/p.width*h);if(d&&(e==="height"||e==="width")){var M=t.style[e];t.style[e]=h+r,_=t[u],M?t.style[e]=M:Ei(t,e)}else(d||a==="%")&&!Kp[je(g,"display")]&&(o.position=je(t,"position")),g===t&&(o.position="static"),g.appendChild(Gi),_=Gi[u],g.removeChild(Gi),o.position="absolute";return l&&d&&(p=qi(g),p.time=Ze.time,p.width=g[u]),pe(f?_*s/h:_&&s?h/_*s:0)},Yn=function(t,e,n,r){var s;return pc||Zo(),e in An&&e!=="transform"&&(e=An[e],~e.indexOf(",")&&(e=e.split(",")[0])),ti[e]&&e!=="transform"?(s=hs(t,r),s=e!=="transformOrigin"?s[e]:s.svg?s.origin:ya(je(t,He))+" "+s.zOrigin+"px"):(s=t.style[e],(!s||s==="auto"||r||~(s+"").indexOf("calc("))&&(s=Sa[e]&&Sa[e](t,e,n)||je(t,e)||Ff(t,e)||(e==="opacity"?1:0))),n&&!~(s+"").trim().indexOf(" ")?Ti(t,e,s,n)+n:s},Zp=function(t,e,n,r){if(!n||n==="none"){var s=Pr(e,t,1),a=s&&je(t,s,1);a&&a!==n?(e=s,n=a):e==="borderColor"&&(n=je(t,"borderTopColor"))}var o=new Ge(this._pt,t.style,e,0,1,fh),l=0,c=0,u,h,f,d,_,g,p,m,M,T,S,b;if(o.b=n,o.e=r,n+="",r+="",r.substring(0,6)==="var(--"&&(r=je(t,r.substring(4,r.indexOf(")")))),r==="auto"&&(g=t.style[e],t.style[e]=r,r=je(t,e)||r,g?t.style[e]=g:Ei(t,e)),u=[n,r],eh(u),n=u[0],r=u[1],f=n.match(gr)||[],b=r.match(gr)||[],b.length){for(;h=gr.exec(r);)p=h[0],M=r.substring(l,h.index),_?_=(_+1)%5:(M.substr(-5)==="rgba("||M.substr(-5)==="hsla(")&&(_=1),p!==(g=f[c++]||"")&&(d=parseFloat(g)||0,S=g.substr((d+"").length),p.charAt(1)==="="&&(p=vr(d,p)+S),m=parseFloat(p),T=p.substr((m+"").length),l=gr.lastIndex-T.length,T||(T=T||Qe.units[e]||S,l===r.length&&(r+=T,o.e+=T)),S!==T&&(d=Ti(t,e,g,T)||0),o._pt={_next:o._pt,p:M||c===1?M:",",s:d,c:m-d,m:_&&_<4||e==="zIndex"?Math.round:0});o.c=l<r.length?r.substring(l,r.length):""}else o.r=e==="display"&&r==="none"?mh:ph;return Df.test(r)&&(o.e=0),this._pt=o,o},au={top:"0%",bottom:"100%",left:"0%",right:"100%",center:"50%"},Jp=function(t){var e=t.split(" "),n=e[0],r=e[1]||"50%";return(n==="top"||n==="bottom"||r==="left"||r==="right")&&(t=n,n=r,r=t),e[0]=au[n]||n,e[1]=au[r]||r,e.join(" ")},jp=function(t,e){if(e.tween&&e.tween._time===e.tween._dur){var n=e.t,r=n.style,s=e.u,a=n._gsap,o,l,c;if(s==="all"||s===!0)r.cssText="",l=1;else for(s=s.split(","),c=s.length;--c>-1;)o=s[c],ti[o]&&(l=1,o=o==="transformOrigin"?He:ce),Ei(n,o);l&&(Ei(n,ce),a&&(a.svg&&n.removeAttribute("transform"),r.scale=r.rotate=r.translate="none",hs(n,1),a.uncache=1,_h(r)))}},Sa={clearProps:function(t,e,n,r,s){if(s.data!=="isFromStart"){var a=t._pt=new Ge(t._pt,e,n,0,0,jp);return a.u=r,a.pr=-10,a.tween=s,t._props.push(n),1}}},fs=[1,0,0,1,0,0],Sh={},yh=function(t){return t==="matrix(1, 0, 0, 1, 0, 0)"||t==="none"||!t},ou=function(t){var e=je(t,ce);return yh(e)?fs:e.substr(7).match(Pf).map(pe)},gc=function(t,e){var n=t._gsap||qi(t),r=t.style,s=ou(t),a,o,l,c;return n.svg&&t.getAttribute("transform")?(l=t.transform.baseVal.consolidate().matrix,s=[l.a,l.b,l.c,l.d,l.e,l.f],s.join(",")==="1,0,0,1,0,0"?fs:s):(s===fs&&!t.offsetParent&&t!==Mr&&!n.svg&&(l=r.display,r.display="block",a=t.parentNode,(!a||!t.offsetParent&&!t.getBoundingClientRect().width)&&(c=1,o=t.nextElementSibling,Mr.appendChild(t)),s=ou(t),l?r.display=l:Ei(t,"display"),c&&(o?a.insertBefore(t,o):a?a.appendChild(t):Mr.removeChild(t))),e&&s.length>6?[s[0],s[1],s[4],s[5],s[12],s[13]]:s)},Jo=function(t,e,n,r,s,a){var o=t._gsap,l=s||gc(t,!0),c=o.xOrigin||0,u=o.yOrigin||0,h=o.xOffset||0,f=o.yOffset||0,d=l[0],_=l[1],g=l[2],p=l[3],m=l[4],M=l[5],T=e.split(" "),S=parseFloat(T[0])||0,b=parseFloat(T[1])||0,A,R,x,y;n?l!==fs&&(R=d*p-_*g)&&(x=S*(p/R)+b*(-g/R)+(g*M-p*m)/R,y=S*(-_/R)+b*(d/R)-(d*M-_*m)/R,S=x,b=y):(A=vh(t),S=A.x+(~T[0].indexOf("%")?S/100*A.width:S),b=A.y+(~(T[1]||T[0]).indexOf("%")?b/100*A.height:b)),r||r!==!1&&o.smooth?(m=S-c,M=b-u,o.xOffset=h+(m*d+M*g)-m,o.yOffset=f+(m*_+M*p)-M):o.xOffset=o.yOffset=0,o.xOrigin=S,o.yOrigin=b,o.smooth=!!r,o.origin=e,o.originIsAbsolute=!!n,t.style[He]="0px 0px",a&&(xi(a,o,"xOrigin",c,S),xi(a,o,"yOrigin",u,b),xi(a,o,"xOffset",h,o.xOffset),xi(a,o,"yOffset",f,o.yOffset)),t.setAttribute("data-svg-origin",S+" "+b)},hs=function(t,e){var n=t._gsap||new sh(t);if("x"in n&&!e&&!n.uncache)return n;var r=t.style,s=n.scaleX<0,a="px",o="deg",l=getComputedStyle(t),c=je(t,He)||"0",u,h,f,d,_,g,p,m,M,T,S,b,A,R,x,y,G,D,B,k,X,C,L,P,z,O,J,Q,st,bt,Ut,Ft;return u=h=f=g=p=m=M=T=S=0,d=_=1,n.svg=!!(t.getCTM&&Mh(t)),l.translate&&((l.translate!=="none"||l.scale!=="none"||l.rotate!=="none")&&(r[ce]=(l.translate!=="none"?"translate3d("+(l.translate+" 0 0").split(" ").slice(0,3).join(", ")+") ":"")+(l.rotate!=="none"?"rotate("+l.rotate+") ":"")+(l.scale!=="none"?"scale("+l.scale.split(" ").join(",")+") ":"")+(l[ce]!=="none"?l[ce]:"")),r.scale=r.rotate=r.translate="none"),R=gc(t,n.svg),n.svg&&(n.uncache?(z=t.getBBox(),c=n.xOrigin-z.x+"px "+(n.yOrigin-z.y)+"px",P=""):P=!e&&t.getAttribute("data-svg-origin"),Jo(t,P||c,!!P||n.originIsAbsolute,n.smooth!==!1,R)),b=n.xOrigin||0,A=n.yOrigin||0,R!==fs&&(D=R[0],B=R[1],k=R[2],X=R[3],u=C=R[4],h=L=R[5],R.length===6?(d=Math.sqrt(D*D+B*B),_=Math.sqrt(X*X+k*k),g=D||B?nr(B,D)*Oi:0,M=k||X?nr(k,X)*Oi+g:0,M&&(_*=Math.abs(Math.cos(M*Sr))),n.svg&&(u-=b-(b*D+A*k),h-=A-(b*B+A*X))):(Ft=R[6],bt=R[7],J=R[8],Q=R[9],st=R[10],Ut=R[11],u=R[12],h=R[13],f=R[14],x=nr(Ft,st),p=x*Oi,x&&(y=Math.cos(-x),G=Math.sin(-x),P=C*y+J*G,z=L*y+Q*G,O=Ft*y+st*G,J=C*-G+J*y,Q=L*-G+Q*y,st=Ft*-G+st*y,Ut=bt*-G+Ut*y,C=P,L=z,Ft=O),x=nr(-k,st),m=x*Oi,x&&(y=Math.cos(-x),G=Math.sin(-x),P=D*y-J*G,z=B*y-Q*G,O=k*y-st*G,Ut=X*G+Ut*y,D=P,B=z,k=O),x=nr(B,D),g=x*Oi,x&&(y=Math.cos(x),G=Math.sin(x),P=D*y+B*G,z=C*y+L*G,B=B*y-D*G,L=L*y-C*G,D=P,C=z),p&&Math.abs(p)+Math.abs(g)>359.9&&(p=g=0,m=180-m),d=pe(Math.sqrt(D*D+B*B+k*k)),_=pe(Math.sqrt(L*L+Ft*Ft)),x=nr(C,L),M=Math.abs(x)>2e-4?x*Oi:0,S=Ut?1/(Ut<0?-Ut:Ut):0),n.svg&&(P=t.getAttribute("transform"),n.forceCSS=t.setAttribute("transform","")||!yh(je(t,ce)),P&&t.setAttribute("transform",P))),Math.abs(M)>90&&Math.abs(M)<270&&(s?(d*=-1,M+=g<=0?180:-180,g+=g<=0?180:-180):(_*=-1,M+=M<=0?180:-180)),e=e||n.uncache,n.x=u-((n.xPercent=u&&(!e&&n.xPercent||(Math.round(t.offsetWidth/2)===Math.round(-u)?-50:0)))?t.offsetWidth*n.xPercent/100:0)+a,n.y=h-((n.yPercent=h&&(!e&&n.yPercent||(Math.round(t.offsetHeight/2)===Math.round(-h)?-50:0)))?t.offsetHeight*n.yPercent/100:0)+a,n.z=f+a,n.scaleX=pe(d),n.scaleY=pe(_),n.rotation=pe(g)+o,n.rotationX=pe(p)+o,n.rotationY=pe(m)+o,n.skewX=M+o,n.skewY=T+o,n.transformPerspective=S+a,(n.zOrigin=parseFloat(c.split(" ")[2])||!e&&n.zOrigin||0)&&(r[He]=ya(c)),n.xOffset=n.yOffset=0,n.force3D=Qe.force3D,n.renderTransform=n.svg?tm:xh?Eh:Qp,n.uncache=0,n},ya=function(t){return(t=t.split(" "))[0]+" "+t[1]},Qa=function(t,e,n){var r=Le(e);return pe(parseFloat(e)+parseFloat(Ti(t,"x",n+"px",r)))+r},Qp=function(t,e){e.z="0px",e.rotationY=e.rotationX="0deg",e.force3D=0,Eh(t,e)},Ci="0deg",Vr="0px",Pi=") ",Eh=function(t,e){var n=e||this,r=n.xPercent,s=n.yPercent,a=n.x,o=n.y,l=n.z,c=n.rotation,u=n.rotationY,h=n.rotationX,f=n.skewX,d=n.skewY,_=n.scaleX,g=n.scaleY,p=n.transformPerspective,m=n.force3D,M=n.target,T=n.zOrigin,S="",b=m==="auto"&&t&&t!==1||m===!0;if(T&&(h!==Ci||u!==Ci)){var A=parseFloat(u)*Sr,R=Math.sin(A),x=Math.cos(A),y;A=parseFloat(h)*Sr,y=Math.cos(A),a=Qa(M,a,R*y*-T),o=Qa(M,o,-Math.sin(A)*-T),l=Qa(M,l,x*y*-T+T)}p!==Vr&&(S+="perspective("+p+Pi),(r||s)&&(S+="translate("+r+"%, "+s+"%) "),(b||a!==Vr||o!==Vr||l!==Vr)&&(S+=l!==Vr||b?"translate3d("+a+", "+o+", "+l+") ":"translate("+a+", "+o+Pi),c!==Ci&&(S+="rotate("+c+Pi),u!==Ci&&(S+="rotateY("+u+Pi),h!==Ci&&(S+="rotateX("+h+Pi),(f!==Ci||d!==Ci)&&(S+="skew("+f+", "+d+Pi),(_!==1||g!==1)&&(S+="scale("+_+", "+g+Pi),M.style[ce]=S||"translate(0, 0)"},tm=function(t,e){var n=e||this,r=n.xPercent,s=n.yPercent,a=n.x,o=n.y,l=n.rotation,c=n.skewX,u=n.skewY,h=n.scaleX,f=n.scaleY,d=n.target,_=n.xOrigin,g=n.yOrigin,p=n.xOffset,m=n.yOffset,M=n.forceCSS,T=parseFloat(a),S=parseFloat(o),b,A,R,x,y;l=parseFloat(l),c=parseFloat(c),u=parseFloat(u),u&&(u=parseFloat(u),c+=u,l+=u),l||c?(l*=Sr,c*=Sr,b=Math.cos(l)*h,A=Math.sin(l)*h,R=Math.sin(l-c)*-f,x=Math.cos(l-c)*f,c&&(u*=Sr,y=Math.tan(c-u),y=Math.sqrt(1+y*y),R*=y,x*=y,u&&(y=Math.tan(u),y=Math.sqrt(1+y*y),b*=y,A*=y)),b=pe(b),A=pe(A),R=pe(R),x=pe(x)):(b=h,x=f,A=R=0),(T&&!~(a+"").indexOf("px")||S&&!~(o+"").indexOf("px"))&&(T=Ti(d,"x",a,"px"),S=Ti(d,"y",o,"px")),(_||g||p||m)&&(T=pe(T+_-(_*b+g*R)+p),S=pe(S+g-(_*A+g*x)+m)),(r||s)&&(y=d.getBBox(),T=pe(T+r/100*y.width),S=pe(S+s/100*y.height)),y="matrix("+b+","+A+","+R+","+x+","+T+","+S+")",d.setAttribute("transform",y),M&&(d.style[ce]=y)},em=function(t,e,n,r,s){var a=360,o=be(s),l=parseFloat(s)*(o&&~s.indexOf("rad")?Oi:1),c=l-r,u=r+c+"deg",h,f;return o&&(h=s.split("_")[1],h==="short"&&(c%=a,c!==c%(a/2)&&(c+=c<0?a:-a)),h==="cw"&&c<0?c=(c+a*eu)%a-~~(c/a)*a:h==="ccw"&&c>0&&(c=(c-a*eu)%a-~~(c/a)*a)),t._pt=f=new Ge(t._pt,e,n,r,c,Op),f.e=u,f.u="deg",t._props.push(n),f},lu=function(t,e){for(var n in e)t[n]=e[n];return t},nm=function(t,e,n){var r=lu({},n._gsap),s="perspective,force3D,transformOrigin,svgOrigin",a=n.style,o,l,c,u,h,f,d,_;r.svg?(c=n.getAttribute("transform"),n.setAttribute("transform",""),a[ce]=e,o=hs(n,1),Ei(n,ce),n.setAttribute("transform",c)):(c=getComputedStyle(n)[ce],a[ce]=e,o=hs(n,1),a[ce]=c);for(l in ti)c=r[l],u=o[l],c!==u&&s.indexOf(l)<0&&(d=Le(c),_=Le(u),h=d!==_?Ti(n,l,c,_):parseFloat(c),f=parseFloat(u),t._pt=new Ge(t._pt,o,l,h,f-h,$o),t._pt.u=_||0,t._props.push(l));lu(o,r)};Ve("padding,margin,Width,Radius",function(i,t){var e="Top",n="Right",r="Bottom",s="Left",a=(t<3?[e,n,r,s]:[e+s,e+n,r+n,r+s]).map(function(o){return t<2?i+o:"border"+o+i});Sa[t>1?"border"+i:i]=function(o,l,c,u,h){var f,d;if(arguments.length<4)return f=a.map(function(_){return Yn(o,_,c)}),d=f.join(" "),d.split(f[0]).length===5?f[0]:d;f=(u+"").split(" "),d={},a.forEach(function(_,g){return d[_]=f[g]=f[g]||f[(g-1)/2|0]}),o.init(l,d,h)}});var Th={name:"css",register:Zo,targetTest:function(t){return t.style&&t.nodeType},init:function(t,e,n,r,s){var a=this._props,o=t.style,l=n.vars.startAt,c,u,h,f,d,_,g,p,m,M,T,S,b,A,R,x,y;pc||Zo(),this.styles=this.styles||gh(t),x=this.styles.props,this.tween=n;for(g in e)if(g!=="autoRound"&&(u=e[g],!(Ke[g]&&ah(g,e,n,r,t,s)))){if(d=typeof u,_=Sa[g],d==="function"&&(u=u.call(n,r,t,s),d=typeof u),d==="string"&&~u.indexOf("random(")&&(u=ls(u)),_)_(this,t,g,u,n)&&(R=1);else if(g.substr(0,2)==="--")c=(getComputedStyle(t).getPropertyValue(g)+"").trim(),u+="",Si.lastIndex=0,Si.test(c)||(p=Le(c),m=Le(u),m?p!==m&&(c=Ti(t,g,c,m)+m):p&&(u+=p)),this.add(o,"setProperty",c,u,r,s,0,0,g),a.push(g),x.push(g,0,o[g]);else if(d!=="undefined"){if(l&&g in l?(c=typeof l[g]=="function"?l[g].call(n,r,t,s):l[g],be(c)&&~c.indexOf("random(")&&(c=ls(c)),Le(c+"")||c==="auto"||(c+=Qe.units[g]||Le(Yn(t,g))||""),(c+"").charAt(1)==="="&&(c=Yn(t,g))):c=Yn(t,g),f=parseFloat(c),M=d==="string"&&u.charAt(1)==="="&&u.substr(0,2),M&&(u=u.substr(2)),h=parseFloat(u),g in An&&(g==="autoAlpha"&&(f===1&&Yn(t,"visibility")==="hidden"&&h&&(f=0),x.push("visibility",0,o.visibility),xi(this,o,"visibility",f?"inherit":"hidden",h?"inherit":"hidden",!h)),g!=="scale"&&g!=="transform"&&(g=An[g],~g.indexOf(",")&&(g=g.split(",")[0]))),T=g in ti,T){if(this.styles.save(g),y=u,d==="string"&&u.substring(0,6)==="var(--"){if(u=je(t,u.substring(4,u.indexOf(")"))),u.substring(0,5)==="calc("){var G=t.style.perspective;t.style.perspective=u,u=je(t,"perspective"),G?t.style.perspective=G:Ei(t,"perspective")}h=parseFloat(u)}if(S||(b=t._gsap,b.renderTransform&&!e.parseTransform||hs(t,e.parseTransform),A=e.smoothOrigin!==!1&&b.smooth,S=this._pt=new Ge(this._pt,o,ce,0,1,b.renderTransform,b,0,-1),S.dep=1),g==="scale")this._pt=new Ge(this._pt,b,"scaleY",b.scaleY,(M?vr(b.scaleY,M+h):h)-b.scaleY||0,$o),this._pt.u=0,a.push("scaleY",g),g+="X";else if(g==="transformOrigin"){x.push(He,0,o[He]),u=Jp(u),b.svg?Jo(t,u,0,A,0,this):(m=parseFloat(u.split(" ")[2])||0,m!==b.zOrigin&&xi(this,b,"zOrigin",b.zOrigin,m),xi(this,o,g,ya(c),ya(u)));continue}else if(g==="svgOrigin"){Jo(t,u,1,A,0,this);continue}else if(g in Sh){em(this,b,g,f,M?vr(f,M+u):u);continue}else if(g==="smoothOrigin"){xi(this,b,"smooth",b.smooth,u);continue}else if(g==="force3D"){b[g]=u;continue}else if(g==="transform"){nm(this,u,t);continue}}else g in o||(g=Pr(g)||g);if(T||(h||h===0)&&(f||f===0)&&!Fp.test(u)&&g in o)p=(c+"").substr((f+"").length),h||(h=0),m=Le(u)||(g in Qe.units?Qe.units[g]:p),p!==m&&(f=Ti(t,g,c,m)),this._pt=new Ge(this._pt,T?b:o,g,f,(M?vr(f,M+h):h)-f,!T&&(m==="px"||g==="zIndex")&&e.autoRound!==!1?zp:$o),this._pt.u=m||0,T&&y!==u?(this._pt.b=c,this._pt.e=y,this._pt.r=kp):p!==m&&m!=="%"&&(this._pt.b=c,this._pt.r=Bp);else if(g in o)Zp.call(this,t,g,c,M?M+u:u);else if(g in t)this.add(t,g,c||t[g],M?M+u:u,r,s);else if(g!=="parseTransform"){rc(g,u);continue}T||(g in o?x.push(g,0,o[g]):typeof t[g]=="function"?x.push(g,2,t[g]()):x.push(g,1,c||t[g])),a.push(g)}}R&&hh(this)},render:function(t,e){if(e.tween._time||!mc())for(var n=e._pt;n;)n.r(t,n.d),n=n._next;else e.styles.revert()},get:Yn,aliases:An,getSetter:function(t,e,n){var r=An[e];return r&&r.indexOf(",")<0&&(e=r),e in ti&&e!==He&&(t._gsap.x||Yn(t,"x"))?n&&tu===n?e==="scale"?Wp:Hp:(tu=n||{})&&(e==="scale"?Xp:qp):t.style&&!ec(t.style[e])?Vp:~e.indexOf("-")?Gp:hc(t,e)},core:{_removeProperty:Ei,_getMatrix:gc}};Xe.utils.checkPrefix=Pr;Xe.core.getStyleSaver=gh;(function(i,t,e,n){var r=Ve(i+","+t+","+e,function(s){ti[s]=1});Ve(t,function(s){Qe.units[s]="deg",Sh[s]=1}),An[r[13]]=i+","+t,Ve(n,function(s){var a=s.split(":");An[a[1]]=r[a[0]]})})("x,y,z,scale,scaleX,scaleY,xPercent,yPercent","rotation,rotationX,rotationY,skewX,skewY","transform,transformOrigin,svgOrigin,force3D,smoothOrigin,transformPerspective","0:translateX,1:translateY,2:translateZ,8:rotate,8:rotationZ,8:rotateZ,9:rotateX,10:rotateY");Ve("x,y,z,top,right,bottom,left,width,height,fontSize,padding,margin,perspective",function(i){Qe.units[i]="px"});Xe.registerPlugin(Th);var ds=Xe.registerPlugin(Th)||Xe;ds.core.Tween;/**
 * @license
 * Copyright 2010-2026 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const xc="183",im=0,cu=1,rm=2,oa=1,sm=2,jr=3,bi=0,We=1,$n=2,Zn=0,yr=1,uu=2,fu=3,hu=4,am=5,zi=100,om=101,lm=102,cm=103,um=104,fm=200,hm=201,dm=202,pm=203,jo=204,Qo=205,mm=206,_m=207,gm=208,xm=209,vm=210,Mm=211,Sm=212,ym=213,Em=214,tl=0,el=1,nl=2,Dr=3,il=4,rl=5,sl=6,al=7,bh=0,Tm=1,bm=2,Cn=0,Ah=1,wh=2,Rh=3,Ch=4,Ph=5,Dh=6,Lh=7,Ih=300,Ji=301,Lr=302,to=303,eo=304,Oa=306,ol=1e3,Kn=1001,ll=1002,we=1003,Am=1004,Ds=1005,Ie=1006,no=1007,Hi=1008,cn=1009,Uh=1010,Nh=1011,ps=1012,vc=1013,Un=1014,wn=1015,ei=1016,Mc=1017,Sc=1018,ms=1020,Fh=35902,Oh=35899,Bh=1021,kh=1022,xn=1023,ni=1026,Wi=1027,zh=1028,yc=1029,Ir=1030,Ec=1031,Tc=1033,la=33776,ca=33777,ua=33778,fa=33779,cl=35840,ul=35841,fl=35842,hl=35843,dl=36196,pl=37492,ml=37496,_l=37488,gl=37489,xl=37490,vl=37491,Ml=37808,Sl=37809,yl=37810,El=37811,Tl=37812,bl=37813,Al=37814,wl=37815,Rl=37816,Cl=37817,Pl=37818,Dl=37819,Ll=37820,Il=37821,Ul=36492,Nl=36494,Fl=36495,Ol=36283,Bl=36284,kl=36285,zl=36286,wm=3200,Rm=0,Cm=1,mi="",on="srgb",Ur="srgb-linear",Ea="linear",Kt="srgb",ir=7680,du=519,Pm=512,Dm=513,Lm=514,bc=515,Im=516,Um=517,Ac=518,Nm=519,pu=35044,mu="300 es",Rn=2e3,Ta=2001;function Fm(i){for(let t=i.length-1;t>=0;--t)if(i[t]>=65535)return!0;return!1}function ba(i){return document.createElementNS("http://www.w3.org/1999/xhtml",i)}function Om(){const i=ba("canvas");return i.style.display="block",i}const _u={};function gu(...i){const t="THREE."+i.shift();console.log(t,...i)}function Vh(i){const t=i[0];if(typeof t=="string"&&t.startsWith("TSL:")){const e=i[1];e&&e.isStackTrace?i[0]+=" "+e.getLocation():i[1]='Stack trace not available. Enable "THREE.Node.captureStackTrace" to capture stack traces.'}return i}function Pt(...i){i=Vh(i);const t="THREE."+i.shift();{const e=i[0];e&&e.isStackTrace?console.warn(e.getError(t)):console.warn(t,...i)}}function Xt(...i){i=Vh(i);const t="THREE."+i.shift();{const e=i[0];e&&e.isStackTrace?console.error(e.getError(t)):console.error(t,...i)}}function Aa(...i){const t=i.join(" ");t in _u||(_u[t]=!0,Pt(...i))}function Bm(i,t,e){return new Promise(function(n,r){function s(){switch(i.clientWaitSync(t,i.SYNC_FLUSH_COMMANDS_BIT,0)){case i.WAIT_FAILED:r();break;case i.TIMEOUT_EXPIRED:setTimeout(s,e);break;default:n()}}setTimeout(s,e)})}const km={[tl]:el,[nl]:sl,[il]:al,[Dr]:rl,[el]:tl,[sl]:nl,[al]:il,[rl]:Dr};class Br{addEventListener(t,e){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[t]===void 0&&(n[t]=[]),n[t].indexOf(e)===-1&&n[t].push(e)}hasEventListener(t,e){const n=this._listeners;return n===void 0?!1:n[t]!==void 0&&n[t].indexOf(e)!==-1}removeEventListener(t,e){const n=this._listeners;if(n===void 0)return;const r=n[t];if(r!==void 0){const s=r.indexOf(e);s!==-1&&r.splice(s,1)}}dispatchEvent(t){const e=this._listeners;if(e===void 0)return;const n=e[t.type];if(n!==void 0){t.target=this;const r=n.slice(0);for(let s=0,a=r.length;s<a;s++)r[s].call(this,t);t.target=null}}}const Pe=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"],io=Math.PI/180,Vl=180/Math.PI;function ys(){const i=Math.random()*4294967295|0,t=Math.random()*4294967295|0,e=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(Pe[i&255]+Pe[i>>8&255]+Pe[i>>16&255]+Pe[i>>24&255]+"-"+Pe[t&255]+Pe[t>>8&255]+"-"+Pe[t>>16&15|64]+Pe[t>>24&255]+"-"+Pe[e&63|128]+Pe[e>>8&255]+"-"+Pe[e>>16&255]+Pe[e>>24&255]+Pe[n&255]+Pe[n>>8&255]+Pe[n>>16&255]+Pe[n>>24&255]).toLowerCase()}function zt(i,t,e){return Math.max(t,Math.min(e,i))}function zm(i,t){return(i%t+t)%t}function ro(i,t,e){return(1-e)*i+e*t}function Gr(i,t){switch(t.constructor){case Float32Array:return i;case Uint32Array:return i/4294967295;case Uint16Array:return i/65535;case Uint8Array:return i/255;case Int32Array:return Math.max(i/2147483647,-1);case Int16Array:return Math.max(i/32767,-1);case Int8Array:return Math.max(i/127,-1);default:throw new Error("Invalid component type.")}}function Be(i,t){switch(t.constructor){case Float32Array:return i;case Uint32Array:return Math.round(i*4294967295);case Uint16Array:return Math.round(i*65535);case Uint8Array:return Math.round(i*255);case Int32Array:return Math.round(i*2147483647);case Int16Array:return Math.round(i*32767);case Int8Array:return Math.round(i*127);default:throw new Error("Invalid component type.")}}class Qt{constructor(t=0,e=0){Qt.prototype.isVector2=!0,this.x=t,this.y=e}get width(){return this.x}set width(t){this.x=t}get height(){return this.y}set height(t){this.y=t}set(t,e){return this.x=t,this.y=e,this}setScalar(t){return this.x=t,this.y=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setComponent(t,e){switch(t){case 0:this.x=e;break;case 1:this.y=e;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y)}copy(t){return this.x=t.x,this.y=t.y,this}add(t){return this.x+=t.x,this.y+=t.y,this}addScalar(t){return this.x+=t,this.y+=t,this}addVectors(t,e){return this.x=t.x+e.x,this.y=t.y+e.y,this}addScaledVector(t,e){return this.x+=t.x*e,this.y+=t.y*e,this}sub(t){return this.x-=t.x,this.y-=t.y,this}subScalar(t){return this.x-=t,this.y-=t,this}subVectors(t,e){return this.x=t.x-e.x,this.y=t.y-e.y,this}multiply(t){return this.x*=t.x,this.y*=t.y,this}multiplyScalar(t){return this.x*=t,this.y*=t,this}divide(t){return this.x/=t.x,this.y/=t.y,this}divideScalar(t){return this.multiplyScalar(1/t)}applyMatrix3(t){const e=this.x,n=this.y,r=t.elements;return this.x=r[0]*e+r[3]*n+r[6],this.y=r[1]*e+r[4]*n+r[7],this}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this}clamp(t,e){return this.x=zt(this.x,t.x,e.x),this.y=zt(this.y,t.y,e.y),this}clampScalar(t,e){return this.x=zt(this.x,t,e),this.y=zt(this.y,t,e),this}clampLength(t,e){const n=this.length();return this.divideScalar(n||1).multiplyScalar(zt(n,t,e))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(t){return this.x*t.x+this.y*t.y}cross(t){return this.x*t.y-this.y*t.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(t){const e=Math.sqrt(this.lengthSq()*t.lengthSq());if(e===0)return Math.PI/2;const n=this.dot(t)/e;return Math.acos(zt(n,-1,1))}distanceTo(t){return Math.sqrt(this.distanceToSquared(t))}distanceToSquared(t){const e=this.x-t.x,n=this.y-t.y;return e*e+n*n}manhattanDistanceTo(t){return Math.abs(this.x-t.x)+Math.abs(this.y-t.y)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,e){return this.x+=(t.x-this.x)*e,this.y+=(t.y-this.y)*e,this}lerpVectors(t,e,n){return this.x=t.x+(e.x-t.x)*n,this.y=t.y+(e.y-t.y)*n,this}equals(t){return t.x===this.x&&t.y===this.y}fromArray(t,e=0){return this.x=t[e],this.y=t[e+1],this}toArray(t=[],e=0){return t[e]=this.x,t[e+1]=this.y,t}fromBufferAttribute(t,e){return this.x=t.getX(e),this.y=t.getY(e),this}rotateAround(t,e){const n=Math.cos(e),r=Math.sin(e),s=this.x-t.x,a=this.y-t.y;return this.x=s*n-a*r+t.x,this.y=s*r+a*n+t.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class kr{constructor(t=0,e=0,n=0,r=1){this.isQuaternion=!0,this._x=t,this._y=e,this._z=n,this._w=r}static slerpFlat(t,e,n,r,s,a,o){let l=n[r+0],c=n[r+1],u=n[r+2],h=n[r+3],f=s[a+0],d=s[a+1],_=s[a+2],g=s[a+3];if(h!==g||l!==f||c!==d||u!==_){let p=l*f+c*d+u*_+h*g;p<0&&(f=-f,d=-d,_=-_,g=-g,p=-p);let m=1-o;if(p<.9995){const M=Math.acos(p),T=Math.sin(M);m=Math.sin(m*M)/T,o=Math.sin(o*M)/T,l=l*m+f*o,c=c*m+d*o,u=u*m+_*o,h=h*m+g*o}else{l=l*m+f*o,c=c*m+d*o,u=u*m+_*o,h=h*m+g*o;const M=1/Math.sqrt(l*l+c*c+u*u+h*h);l*=M,c*=M,u*=M,h*=M}}t[e]=l,t[e+1]=c,t[e+2]=u,t[e+3]=h}static multiplyQuaternionsFlat(t,e,n,r,s,a){const o=n[r],l=n[r+1],c=n[r+2],u=n[r+3],h=s[a],f=s[a+1],d=s[a+2],_=s[a+3];return t[e]=o*_+u*h+l*d-c*f,t[e+1]=l*_+u*f+c*h-o*d,t[e+2]=c*_+u*d+o*f-l*h,t[e+3]=u*_-o*h-l*f-c*d,t}get x(){return this._x}set x(t){this._x=t,this._onChangeCallback()}get y(){return this._y}set y(t){this._y=t,this._onChangeCallback()}get z(){return this._z}set z(t){this._z=t,this._onChangeCallback()}get w(){return this._w}set w(t){this._w=t,this._onChangeCallback()}set(t,e,n,r){return this._x=t,this._y=e,this._z=n,this._w=r,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(t){return this._x=t.x,this._y=t.y,this._z=t.z,this._w=t.w,this._onChangeCallback(),this}setFromEuler(t,e=!0){const n=t._x,r=t._y,s=t._z,a=t._order,o=Math.cos,l=Math.sin,c=o(n/2),u=o(r/2),h=o(s/2),f=l(n/2),d=l(r/2),_=l(s/2);switch(a){case"XYZ":this._x=f*u*h+c*d*_,this._y=c*d*h-f*u*_,this._z=c*u*_+f*d*h,this._w=c*u*h-f*d*_;break;case"YXZ":this._x=f*u*h+c*d*_,this._y=c*d*h-f*u*_,this._z=c*u*_-f*d*h,this._w=c*u*h+f*d*_;break;case"ZXY":this._x=f*u*h-c*d*_,this._y=c*d*h+f*u*_,this._z=c*u*_+f*d*h,this._w=c*u*h-f*d*_;break;case"ZYX":this._x=f*u*h-c*d*_,this._y=c*d*h+f*u*_,this._z=c*u*_-f*d*h,this._w=c*u*h+f*d*_;break;case"YZX":this._x=f*u*h+c*d*_,this._y=c*d*h+f*u*_,this._z=c*u*_-f*d*h,this._w=c*u*h-f*d*_;break;case"XZY":this._x=f*u*h-c*d*_,this._y=c*d*h-f*u*_,this._z=c*u*_+f*d*h,this._w=c*u*h+f*d*_;break;default:Pt("Quaternion: .setFromEuler() encountered an unknown order: "+a)}return e===!0&&this._onChangeCallback(),this}setFromAxisAngle(t,e){const n=e/2,r=Math.sin(n);return this._x=t.x*r,this._y=t.y*r,this._z=t.z*r,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(t){const e=t.elements,n=e[0],r=e[4],s=e[8],a=e[1],o=e[5],l=e[9],c=e[2],u=e[6],h=e[10],f=n+o+h;if(f>0){const d=.5/Math.sqrt(f+1);this._w=.25/d,this._x=(u-l)*d,this._y=(s-c)*d,this._z=(a-r)*d}else if(n>o&&n>h){const d=2*Math.sqrt(1+n-o-h);this._w=(u-l)/d,this._x=.25*d,this._y=(r+a)/d,this._z=(s+c)/d}else if(o>h){const d=2*Math.sqrt(1+o-n-h);this._w=(s-c)/d,this._x=(r+a)/d,this._y=.25*d,this._z=(l+u)/d}else{const d=2*Math.sqrt(1+h-n-o);this._w=(a-r)/d,this._x=(s+c)/d,this._y=(l+u)/d,this._z=.25*d}return this._onChangeCallback(),this}setFromUnitVectors(t,e){let n=t.dot(e)+1;return n<1e-8?(n=0,Math.abs(t.x)>Math.abs(t.z)?(this._x=-t.y,this._y=t.x,this._z=0,this._w=n):(this._x=0,this._y=-t.z,this._z=t.y,this._w=n)):(this._x=t.y*e.z-t.z*e.y,this._y=t.z*e.x-t.x*e.z,this._z=t.x*e.y-t.y*e.x,this._w=n),this.normalize()}angleTo(t){return 2*Math.acos(Math.abs(zt(this.dot(t),-1,1)))}rotateTowards(t,e){const n=this.angleTo(t);if(n===0)return this;const r=Math.min(1,e/n);return this.slerp(t,r),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(t){return this._x*t._x+this._y*t._y+this._z*t._z+this._w*t._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let t=this.length();return t===0?(this._x=0,this._y=0,this._z=0,this._w=1):(t=1/t,this._x=this._x*t,this._y=this._y*t,this._z=this._z*t,this._w=this._w*t),this._onChangeCallback(),this}multiply(t){return this.multiplyQuaternions(this,t)}premultiply(t){return this.multiplyQuaternions(t,this)}multiplyQuaternions(t,e){const n=t._x,r=t._y,s=t._z,a=t._w,o=e._x,l=e._y,c=e._z,u=e._w;return this._x=n*u+a*o+r*c-s*l,this._y=r*u+a*l+s*o-n*c,this._z=s*u+a*c+n*l-r*o,this._w=a*u-n*o-r*l-s*c,this._onChangeCallback(),this}slerp(t,e){let n=t._x,r=t._y,s=t._z,a=t._w,o=this.dot(t);o<0&&(n=-n,r=-r,s=-s,a=-a,o=-o);let l=1-e;if(o<.9995){const c=Math.acos(o),u=Math.sin(c);l=Math.sin(l*c)/u,e=Math.sin(e*c)/u,this._x=this._x*l+n*e,this._y=this._y*l+r*e,this._z=this._z*l+s*e,this._w=this._w*l+a*e,this._onChangeCallback()}else this._x=this._x*l+n*e,this._y=this._y*l+r*e,this._z=this._z*l+s*e,this._w=this._w*l+a*e,this.normalize();return this}slerpQuaternions(t,e,n){return this.copy(t).slerp(e,n)}random(){const t=2*Math.PI*Math.random(),e=2*Math.PI*Math.random(),n=Math.random(),r=Math.sqrt(1-n),s=Math.sqrt(n);return this.set(r*Math.sin(t),r*Math.cos(t),s*Math.sin(e),s*Math.cos(e))}equals(t){return t._x===this._x&&t._y===this._y&&t._z===this._z&&t._w===this._w}fromArray(t,e=0){return this._x=t[e],this._y=t[e+1],this._z=t[e+2],this._w=t[e+3],this._onChangeCallback(),this}toArray(t=[],e=0){return t[e]=this._x,t[e+1]=this._y,t[e+2]=this._z,t[e+3]=this._w,t}fromBufferAttribute(t,e){return this._x=t.getX(e),this._y=t.getY(e),this._z=t.getZ(e),this._w=t.getW(e),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(t){return this._onChangeCallback=t,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class W{constructor(t=0,e=0,n=0){W.prototype.isVector3=!0,this.x=t,this.y=e,this.z=n}set(t,e,n){return n===void 0&&(n=this.z),this.x=t,this.y=e,this.z=n,this}setScalar(t){return this.x=t,this.y=t,this.z=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setZ(t){return this.z=t,this}setComponent(t,e){switch(t){case 0:this.x=e;break;case 1:this.y=e;break;case 2:this.z=e;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(t){return this.x=t.x,this.y=t.y,this.z=t.z,this}add(t){return this.x+=t.x,this.y+=t.y,this.z+=t.z,this}addScalar(t){return this.x+=t,this.y+=t,this.z+=t,this}addVectors(t,e){return this.x=t.x+e.x,this.y=t.y+e.y,this.z=t.z+e.z,this}addScaledVector(t,e){return this.x+=t.x*e,this.y+=t.y*e,this.z+=t.z*e,this}sub(t){return this.x-=t.x,this.y-=t.y,this.z-=t.z,this}subScalar(t){return this.x-=t,this.y-=t,this.z-=t,this}subVectors(t,e){return this.x=t.x-e.x,this.y=t.y-e.y,this.z=t.z-e.z,this}multiply(t){return this.x*=t.x,this.y*=t.y,this.z*=t.z,this}multiplyScalar(t){return this.x*=t,this.y*=t,this.z*=t,this}multiplyVectors(t,e){return this.x=t.x*e.x,this.y=t.y*e.y,this.z=t.z*e.z,this}applyEuler(t){return this.applyQuaternion(xu.setFromEuler(t))}applyAxisAngle(t,e){return this.applyQuaternion(xu.setFromAxisAngle(t,e))}applyMatrix3(t){const e=this.x,n=this.y,r=this.z,s=t.elements;return this.x=s[0]*e+s[3]*n+s[6]*r,this.y=s[1]*e+s[4]*n+s[7]*r,this.z=s[2]*e+s[5]*n+s[8]*r,this}applyNormalMatrix(t){return this.applyMatrix3(t).normalize()}applyMatrix4(t){const e=this.x,n=this.y,r=this.z,s=t.elements,a=1/(s[3]*e+s[7]*n+s[11]*r+s[15]);return this.x=(s[0]*e+s[4]*n+s[8]*r+s[12])*a,this.y=(s[1]*e+s[5]*n+s[9]*r+s[13])*a,this.z=(s[2]*e+s[6]*n+s[10]*r+s[14])*a,this}applyQuaternion(t){const e=this.x,n=this.y,r=this.z,s=t.x,a=t.y,o=t.z,l=t.w,c=2*(a*r-o*n),u=2*(o*e-s*r),h=2*(s*n-a*e);return this.x=e+l*c+a*h-o*u,this.y=n+l*u+o*c-s*h,this.z=r+l*h+s*u-a*c,this}project(t){return this.applyMatrix4(t.matrixWorldInverse).applyMatrix4(t.projectionMatrix)}unproject(t){return this.applyMatrix4(t.projectionMatrixInverse).applyMatrix4(t.matrixWorld)}transformDirection(t){const e=this.x,n=this.y,r=this.z,s=t.elements;return this.x=s[0]*e+s[4]*n+s[8]*r,this.y=s[1]*e+s[5]*n+s[9]*r,this.z=s[2]*e+s[6]*n+s[10]*r,this.normalize()}divide(t){return this.x/=t.x,this.y/=t.y,this.z/=t.z,this}divideScalar(t){return this.multiplyScalar(1/t)}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this.z=Math.min(this.z,t.z),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this.z=Math.max(this.z,t.z),this}clamp(t,e){return this.x=zt(this.x,t.x,e.x),this.y=zt(this.y,t.y,e.y),this.z=zt(this.z,t.z,e.z),this}clampScalar(t,e){return this.x=zt(this.x,t,e),this.y=zt(this.y,t,e),this.z=zt(this.z,t,e),this}clampLength(t,e){const n=this.length();return this.divideScalar(n||1).multiplyScalar(zt(n,t,e))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(t){return this.x*t.x+this.y*t.y+this.z*t.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,e){return this.x+=(t.x-this.x)*e,this.y+=(t.y-this.y)*e,this.z+=(t.z-this.z)*e,this}lerpVectors(t,e,n){return this.x=t.x+(e.x-t.x)*n,this.y=t.y+(e.y-t.y)*n,this.z=t.z+(e.z-t.z)*n,this}cross(t){return this.crossVectors(this,t)}crossVectors(t,e){const n=t.x,r=t.y,s=t.z,a=e.x,o=e.y,l=e.z;return this.x=r*l-s*o,this.y=s*a-n*l,this.z=n*o-r*a,this}projectOnVector(t){const e=t.lengthSq();if(e===0)return this.set(0,0,0);const n=t.dot(this)/e;return this.copy(t).multiplyScalar(n)}projectOnPlane(t){return so.copy(this).projectOnVector(t),this.sub(so)}reflect(t){return this.sub(so.copy(t).multiplyScalar(2*this.dot(t)))}angleTo(t){const e=Math.sqrt(this.lengthSq()*t.lengthSq());if(e===0)return Math.PI/2;const n=this.dot(t)/e;return Math.acos(zt(n,-1,1))}distanceTo(t){return Math.sqrt(this.distanceToSquared(t))}distanceToSquared(t){const e=this.x-t.x,n=this.y-t.y,r=this.z-t.z;return e*e+n*n+r*r}manhattanDistanceTo(t){return Math.abs(this.x-t.x)+Math.abs(this.y-t.y)+Math.abs(this.z-t.z)}setFromSpherical(t){return this.setFromSphericalCoords(t.radius,t.phi,t.theta)}setFromSphericalCoords(t,e,n){const r=Math.sin(e)*t;return this.x=r*Math.sin(n),this.y=Math.cos(e)*t,this.z=r*Math.cos(n),this}setFromCylindrical(t){return this.setFromCylindricalCoords(t.radius,t.theta,t.y)}setFromCylindricalCoords(t,e,n){return this.x=t*Math.sin(e),this.y=n,this.z=t*Math.cos(e),this}setFromMatrixPosition(t){const e=t.elements;return this.x=e[12],this.y=e[13],this.z=e[14],this}setFromMatrixScale(t){const e=this.setFromMatrixColumn(t,0).length(),n=this.setFromMatrixColumn(t,1).length(),r=this.setFromMatrixColumn(t,2).length();return this.x=e,this.y=n,this.z=r,this}setFromMatrixColumn(t,e){return this.fromArray(t.elements,e*4)}setFromMatrix3Column(t,e){return this.fromArray(t.elements,e*3)}setFromEuler(t){return this.x=t._x,this.y=t._y,this.z=t._z,this}setFromColor(t){return this.x=t.r,this.y=t.g,this.z=t.b,this}equals(t){return t.x===this.x&&t.y===this.y&&t.z===this.z}fromArray(t,e=0){return this.x=t[e],this.y=t[e+1],this.z=t[e+2],this}toArray(t=[],e=0){return t[e]=this.x,t[e+1]=this.y,t[e+2]=this.z,t}fromBufferAttribute(t,e){return this.x=t.getX(e),this.y=t.getY(e),this.z=t.getZ(e),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const t=Math.random()*Math.PI*2,e=Math.random()*2-1,n=Math.sqrt(1-e*e);return this.x=n*Math.cos(t),this.y=e,this.z=n*Math.sin(t),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const so=new W,xu=new kr;class It{constructor(t,e,n,r,s,a,o,l,c){It.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],t!==void 0&&this.set(t,e,n,r,s,a,o,l,c)}set(t,e,n,r,s,a,o,l,c){const u=this.elements;return u[0]=t,u[1]=r,u[2]=o,u[3]=e,u[4]=s,u[5]=l,u[6]=n,u[7]=a,u[8]=c,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(t){const e=this.elements,n=t.elements;return e[0]=n[0],e[1]=n[1],e[2]=n[2],e[3]=n[3],e[4]=n[4],e[5]=n[5],e[6]=n[6],e[7]=n[7],e[8]=n[8],this}extractBasis(t,e,n){return t.setFromMatrix3Column(this,0),e.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(t){const e=t.elements;return this.set(e[0],e[4],e[8],e[1],e[5],e[9],e[2],e[6],e[10]),this}multiply(t){return this.multiplyMatrices(this,t)}premultiply(t){return this.multiplyMatrices(t,this)}multiplyMatrices(t,e){const n=t.elements,r=e.elements,s=this.elements,a=n[0],o=n[3],l=n[6],c=n[1],u=n[4],h=n[7],f=n[2],d=n[5],_=n[8],g=r[0],p=r[3],m=r[6],M=r[1],T=r[4],S=r[7],b=r[2],A=r[5],R=r[8];return s[0]=a*g+o*M+l*b,s[3]=a*p+o*T+l*A,s[6]=a*m+o*S+l*R,s[1]=c*g+u*M+h*b,s[4]=c*p+u*T+h*A,s[7]=c*m+u*S+h*R,s[2]=f*g+d*M+_*b,s[5]=f*p+d*T+_*A,s[8]=f*m+d*S+_*R,this}multiplyScalar(t){const e=this.elements;return e[0]*=t,e[3]*=t,e[6]*=t,e[1]*=t,e[4]*=t,e[7]*=t,e[2]*=t,e[5]*=t,e[8]*=t,this}determinant(){const t=this.elements,e=t[0],n=t[1],r=t[2],s=t[3],a=t[4],o=t[5],l=t[6],c=t[7],u=t[8];return e*a*u-e*o*c-n*s*u+n*o*l+r*s*c-r*a*l}invert(){const t=this.elements,e=t[0],n=t[1],r=t[2],s=t[3],a=t[4],o=t[5],l=t[6],c=t[7],u=t[8],h=u*a-o*c,f=o*l-u*s,d=c*s-a*l,_=e*h+n*f+r*d;if(_===0)return this.set(0,0,0,0,0,0,0,0,0);const g=1/_;return t[0]=h*g,t[1]=(r*c-u*n)*g,t[2]=(o*n-r*a)*g,t[3]=f*g,t[4]=(u*e-r*l)*g,t[5]=(r*s-o*e)*g,t[6]=d*g,t[7]=(n*l-c*e)*g,t[8]=(a*e-n*s)*g,this}transpose(){let t;const e=this.elements;return t=e[1],e[1]=e[3],e[3]=t,t=e[2],e[2]=e[6],e[6]=t,t=e[5],e[5]=e[7],e[7]=t,this}getNormalMatrix(t){return this.setFromMatrix4(t).invert().transpose()}transposeIntoArray(t){const e=this.elements;return t[0]=e[0],t[1]=e[3],t[2]=e[6],t[3]=e[1],t[4]=e[4],t[5]=e[7],t[6]=e[2],t[7]=e[5],t[8]=e[8],this}setUvTransform(t,e,n,r,s,a,o){const l=Math.cos(s),c=Math.sin(s);return this.set(n*l,n*c,-n*(l*a+c*o)+a+t,-r*c,r*l,-r*(-c*a+l*o)+o+e,0,0,1),this}scale(t,e){return this.premultiply(ao.makeScale(t,e)),this}rotate(t){return this.premultiply(ao.makeRotation(-t)),this}translate(t,e){return this.premultiply(ao.makeTranslation(t,e)),this}makeTranslation(t,e){return t.isVector2?this.set(1,0,t.x,0,1,t.y,0,0,1):this.set(1,0,t,0,1,e,0,0,1),this}makeRotation(t){const e=Math.cos(t),n=Math.sin(t);return this.set(e,-n,0,n,e,0,0,0,1),this}makeScale(t,e){return this.set(t,0,0,0,e,0,0,0,1),this}equals(t){const e=this.elements,n=t.elements;for(let r=0;r<9;r++)if(e[r]!==n[r])return!1;return!0}fromArray(t,e=0){for(let n=0;n<9;n++)this.elements[n]=t[n+e];return this}toArray(t=[],e=0){const n=this.elements;return t[e]=n[0],t[e+1]=n[1],t[e+2]=n[2],t[e+3]=n[3],t[e+4]=n[4],t[e+5]=n[5],t[e+6]=n[6],t[e+7]=n[7],t[e+8]=n[8],t}clone(){return new this.constructor().fromArray(this.elements)}}const ao=new It,vu=new It().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),Mu=new It().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);function Vm(){const i={enabled:!0,workingColorSpace:Ur,spaces:{},convert:function(r,s,a){return this.enabled===!1||s===a||!s||!a||(this.spaces[s].transfer===Kt&&(r.r=Jn(r.r),r.g=Jn(r.g),r.b=Jn(r.b)),this.spaces[s].primaries!==this.spaces[a].primaries&&(r.applyMatrix3(this.spaces[s].toXYZ),r.applyMatrix3(this.spaces[a].fromXYZ)),this.spaces[a].transfer===Kt&&(r.r=Er(r.r),r.g=Er(r.g),r.b=Er(r.b))),r},workingToColorSpace:function(r,s){return this.convert(r,this.workingColorSpace,s)},colorSpaceToWorking:function(r,s){return this.convert(r,s,this.workingColorSpace)},getPrimaries:function(r){return this.spaces[r].primaries},getTransfer:function(r){return r===mi?Ea:this.spaces[r].transfer},getToneMappingMode:function(r){return this.spaces[r].outputColorSpaceConfig.toneMappingMode||"standard"},getLuminanceCoefficients:function(r,s=this.workingColorSpace){return r.fromArray(this.spaces[s].luminanceCoefficients)},define:function(r){Object.assign(this.spaces,r)},_getMatrix:function(r,s,a){return r.copy(this.spaces[s].toXYZ).multiply(this.spaces[a].fromXYZ)},_getDrawingBufferColorSpace:function(r){return this.spaces[r].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(r=this.workingColorSpace){return this.spaces[r].workingColorSpaceConfig.unpackColorSpace},fromWorkingColorSpace:function(r,s){return Aa("ColorManagement: .fromWorkingColorSpace() has been renamed to .workingToColorSpace()."),i.workingToColorSpace(r,s)},toWorkingColorSpace:function(r,s){return Aa("ColorManagement: .toWorkingColorSpace() has been renamed to .colorSpaceToWorking()."),i.colorSpaceToWorking(r,s)}},t=[.64,.33,.3,.6,.15,.06],e=[.2126,.7152,.0722],n=[.3127,.329];return i.define({[Ur]:{primaries:t,whitePoint:n,transfer:Ea,toXYZ:vu,fromXYZ:Mu,luminanceCoefficients:e,workingColorSpaceConfig:{unpackColorSpace:on},outputColorSpaceConfig:{drawingBufferColorSpace:on}},[on]:{primaries:t,whitePoint:n,transfer:Kt,toXYZ:vu,fromXYZ:Mu,luminanceCoefficients:e,outputColorSpaceConfig:{drawingBufferColorSpace:on}}}),i}const Ht=Vm();function Jn(i){return i<.04045?i*.0773993808:Math.pow(i*.9478672986+.0521327014,2.4)}function Er(i){return i<.0031308?i*12.92:1.055*Math.pow(i,.41666)-.055}let rr;class Gm{static getDataURL(t,e="image/png"){if(/^data:/i.test(t.src)||typeof HTMLCanvasElement>"u")return t.src;let n;if(t instanceof HTMLCanvasElement)n=t;else{rr===void 0&&(rr=ba("canvas")),rr.width=t.width,rr.height=t.height;const r=rr.getContext("2d");t instanceof ImageData?r.putImageData(t,0,0):r.drawImage(t,0,0,t.width,t.height),n=rr}return n.toDataURL(e)}static sRGBToLinear(t){if(typeof HTMLImageElement<"u"&&t instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&t instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&t instanceof ImageBitmap){const e=ba("canvas");e.width=t.width,e.height=t.height;const n=e.getContext("2d");n.drawImage(t,0,0,t.width,t.height);const r=n.getImageData(0,0,t.width,t.height),s=r.data;for(let a=0;a<s.length;a++)s[a]=Jn(s[a]/255)*255;return n.putImageData(r,0,0),e}else if(t.data){const e=t.data.slice(0);for(let n=0;n<e.length;n++)e instanceof Uint8Array||e instanceof Uint8ClampedArray?e[n]=Math.floor(Jn(e[n]/255)*255):e[n]=Jn(e[n]);return{data:e,width:t.width,height:t.height}}else return Pt("ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),t}}let Hm=0;class wc{constructor(t=null){this.isSource=!0,Object.defineProperty(this,"id",{value:Hm++}),this.uuid=ys(),this.data=t,this.dataReady=!0,this.version=0}getSize(t){const e=this.data;return typeof HTMLVideoElement<"u"&&e instanceof HTMLVideoElement?t.set(e.videoWidth,e.videoHeight,0):typeof VideoFrame<"u"&&e instanceof VideoFrame?t.set(e.displayHeight,e.displayWidth,0):e!==null?t.set(e.width,e.height,e.depth||0):t.set(0,0,0),t}set needsUpdate(t){t===!0&&this.version++}toJSON(t){const e=t===void 0||typeof t=="string";if(!e&&t.images[this.uuid]!==void 0)return t.images[this.uuid];const n={uuid:this.uuid,url:""},r=this.data;if(r!==null){let s;if(Array.isArray(r)){s=[];for(let a=0,o=r.length;a<o;a++)r[a].isDataTexture?s.push(oo(r[a].image)):s.push(oo(r[a]))}else s=oo(r);n.url=s}return e||(t.images[this.uuid]=n),n}}function oo(i){return typeof HTMLImageElement<"u"&&i instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&i instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&i instanceof ImageBitmap?Gm.getDataURL(i):i.data?{data:Array.from(i.data),width:i.width,height:i.height,type:i.data.constructor.name}:(Pt("Texture: Unable to serialize Texture."),{})}let Wm=0;const lo=new W;class Oe extends Br{constructor(t=Oe.DEFAULT_IMAGE,e=Oe.DEFAULT_MAPPING,n=Kn,r=Kn,s=Ie,a=Hi,o=xn,l=cn,c=Oe.DEFAULT_ANISOTROPY,u=mi){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:Wm++}),this.uuid=ys(),this.name="",this.source=new wc(t),this.mipmaps=[],this.mapping=e,this.channel=0,this.wrapS=n,this.wrapT=r,this.magFilter=s,this.minFilter=a,this.anisotropy=c,this.format=o,this.internalFormat=null,this.type=l,this.offset=new Qt(0,0),this.repeat=new Qt(1,1),this.center=new Qt(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new It,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=u,this.userData={},this.updateRanges=[],this.version=0,this.onUpdate=null,this.renderTarget=null,this.isRenderTargetTexture=!1,this.isArrayTexture=!!(t&&t.depth&&t.depth>1),this.pmremVersion=0}get width(){return this.source.getSize(lo).x}get height(){return this.source.getSize(lo).y}get depth(){return this.source.getSize(lo).z}get image(){return this.source.data}set image(t=null){this.source.data=t}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}addUpdateRange(t,e){this.updateRanges.push({start:t,count:e})}clearUpdateRanges(){this.updateRanges.length=0}clone(){return new this.constructor().copy(this)}copy(t){return this.name=t.name,this.source=t.source,this.mipmaps=t.mipmaps.slice(0),this.mapping=t.mapping,this.channel=t.channel,this.wrapS=t.wrapS,this.wrapT=t.wrapT,this.magFilter=t.magFilter,this.minFilter=t.minFilter,this.anisotropy=t.anisotropy,this.format=t.format,this.internalFormat=t.internalFormat,this.type=t.type,this.offset.copy(t.offset),this.repeat.copy(t.repeat),this.center.copy(t.center),this.rotation=t.rotation,this.matrixAutoUpdate=t.matrixAutoUpdate,this.matrix.copy(t.matrix),this.generateMipmaps=t.generateMipmaps,this.premultiplyAlpha=t.premultiplyAlpha,this.flipY=t.flipY,this.unpackAlignment=t.unpackAlignment,this.colorSpace=t.colorSpace,this.renderTarget=t.renderTarget,this.isRenderTargetTexture=t.isRenderTargetTexture,this.isArrayTexture=t.isArrayTexture,this.userData=JSON.parse(JSON.stringify(t.userData)),this.needsUpdate=!0,this}setValues(t){for(const e in t){const n=t[e];if(n===void 0){Pt(`Texture.setValues(): parameter '${e}' has value of undefined.`);continue}const r=this[e];if(r===void 0){Pt(`Texture.setValues(): property '${e}' does not exist.`);continue}r&&n&&r.isVector2&&n.isVector2||r&&n&&r.isVector3&&n.isVector3||r&&n&&r.isMatrix3&&n.isMatrix3?r.copy(n):this[e]=n}}toJSON(t){const e=t===void 0||typeof t=="string";if(!e&&t.textures[this.uuid]!==void 0)return t.textures[this.uuid];const n={metadata:{version:4.7,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(t).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),e||(t.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(t){if(this.mapping!==Ih)return t;if(t.applyMatrix3(this.matrix),t.x<0||t.x>1)switch(this.wrapS){case ol:t.x=t.x-Math.floor(t.x);break;case Kn:t.x=t.x<0?0:1;break;case ll:Math.abs(Math.floor(t.x)%2)===1?t.x=Math.ceil(t.x)-t.x:t.x=t.x-Math.floor(t.x);break}if(t.y<0||t.y>1)switch(this.wrapT){case ol:t.y=t.y-Math.floor(t.y);break;case Kn:t.y=t.y<0?0:1;break;case ll:Math.abs(Math.floor(t.y)%2)===1?t.y=Math.ceil(t.y)-t.y:t.y=t.y-Math.floor(t.y);break}return this.flipY&&(t.y=1-t.y),t}set needsUpdate(t){t===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(t){t===!0&&this.pmremVersion++}}Oe.DEFAULT_IMAGE=null;Oe.DEFAULT_MAPPING=Ih;Oe.DEFAULT_ANISOTROPY=1;class me{constructor(t=0,e=0,n=0,r=1){me.prototype.isVector4=!0,this.x=t,this.y=e,this.z=n,this.w=r}get width(){return this.z}set width(t){this.z=t}get height(){return this.w}set height(t){this.w=t}set(t,e,n,r){return this.x=t,this.y=e,this.z=n,this.w=r,this}setScalar(t){return this.x=t,this.y=t,this.z=t,this.w=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setZ(t){return this.z=t,this}setW(t){return this.w=t,this}setComponent(t,e){switch(t){case 0:this.x=e;break;case 1:this.y=e;break;case 2:this.z=e;break;case 3:this.w=e;break;default:throw new Error("index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(t){return this.x=t.x,this.y=t.y,this.z=t.z,this.w=t.w!==void 0?t.w:1,this}add(t){return this.x+=t.x,this.y+=t.y,this.z+=t.z,this.w+=t.w,this}addScalar(t){return this.x+=t,this.y+=t,this.z+=t,this.w+=t,this}addVectors(t,e){return this.x=t.x+e.x,this.y=t.y+e.y,this.z=t.z+e.z,this.w=t.w+e.w,this}addScaledVector(t,e){return this.x+=t.x*e,this.y+=t.y*e,this.z+=t.z*e,this.w+=t.w*e,this}sub(t){return this.x-=t.x,this.y-=t.y,this.z-=t.z,this.w-=t.w,this}subScalar(t){return this.x-=t,this.y-=t,this.z-=t,this.w-=t,this}subVectors(t,e){return this.x=t.x-e.x,this.y=t.y-e.y,this.z=t.z-e.z,this.w=t.w-e.w,this}multiply(t){return this.x*=t.x,this.y*=t.y,this.z*=t.z,this.w*=t.w,this}multiplyScalar(t){return this.x*=t,this.y*=t,this.z*=t,this.w*=t,this}applyMatrix4(t){const e=this.x,n=this.y,r=this.z,s=this.w,a=t.elements;return this.x=a[0]*e+a[4]*n+a[8]*r+a[12]*s,this.y=a[1]*e+a[5]*n+a[9]*r+a[13]*s,this.z=a[2]*e+a[6]*n+a[10]*r+a[14]*s,this.w=a[3]*e+a[7]*n+a[11]*r+a[15]*s,this}divide(t){return this.x/=t.x,this.y/=t.y,this.z/=t.z,this.w/=t.w,this}divideScalar(t){return this.multiplyScalar(1/t)}setAxisAngleFromQuaternion(t){this.w=2*Math.acos(t.w);const e=Math.sqrt(1-t.w*t.w);return e<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=t.x/e,this.y=t.y/e,this.z=t.z/e),this}setAxisAngleFromRotationMatrix(t){let e,n,r,s;const l=t.elements,c=l[0],u=l[4],h=l[8],f=l[1],d=l[5],_=l[9],g=l[2],p=l[6],m=l[10];if(Math.abs(u-f)<.01&&Math.abs(h-g)<.01&&Math.abs(_-p)<.01){if(Math.abs(u+f)<.1&&Math.abs(h+g)<.1&&Math.abs(_+p)<.1&&Math.abs(c+d+m-3)<.1)return this.set(1,0,0,0),this;e=Math.PI;const T=(c+1)/2,S=(d+1)/2,b=(m+1)/2,A=(u+f)/4,R=(h+g)/4,x=(_+p)/4;return T>S&&T>b?T<.01?(n=0,r=.707106781,s=.707106781):(n=Math.sqrt(T),r=A/n,s=R/n):S>b?S<.01?(n=.707106781,r=0,s=.707106781):(r=Math.sqrt(S),n=A/r,s=x/r):b<.01?(n=.707106781,r=.707106781,s=0):(s=Math.sqrt(b),n=R/s,r=x/s),this.set(n,r,s,e),this}let M=Math.sqrt((p-_)*(p-_)+(h-g)*(h-g)+(f-u)*(f-u));return Math.abs(M)<.001&&(M=1),this.x=(p-_)/M,this.y=(h-g)/M,this.z=(f-u)/M,this.w=Math.acos((c+d+m-1)/2),this}setFromMatrixPosition(t){const e=t.elements;return this.x=e[12],this.y=e[13],this.z=e[14],this.w=e[15],this}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this.z=Math.min(this.z,t.z),this.w=Math.min(this.w,t.w),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this.z=Math.max(this.z,t.z),this.w=Math.max(this.w,t.w),this}clamp(t,e){return this.x=zt(this.x,t.x,e.x),this.y=zt(this.y,t.y,e.y),this.z=zt(this.z,t.z,e.z),this.w=zt(this.w,t.w,e.w),this}clampScalar(t,e){return this.x=zt(this.x,t,e),this.y=zt(this.y,t,e),this.z=zt(this.z,t,e),this.w=zt(this.w,t,e),this}clampLength(t,e){const n=this.length();return this.divideScalar(n||1).multiplyScalar(zt(n,t,e))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(t){return this.x*t.x+this.y*t.y+this.z*t.z+this.w*t.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,e){return this.x+=(t.x-this.x)*e,this.y+=(t.y-this.y)*e,this.z+=(t.z-this.z)*e,this.w+=(t.w-this.w)*e,this}lerpVectors(t,e,n){return this.x=t.x+(e.x-t.x)*n,this.y=t.y+(e.y-t.y)*n,this.z=t.z+(e.z-t.z)*n,this.w=t.w+(e.w-t.w)*n,this}equals(t){return t.x===this.x&&t.y===this.y&&t.z===this.z&&t.w===this.w}fromArray(t,e=0){return this.x=t[e],this.y=t[e+1],this.z=t[e+2],this.w=t[e+3],this}toArray(t=[],e=0){return t[e]=this.x,t[e+1]=this.y,t[e+2]=this.z,t[e+3]=this.w,t}fromBufferAttribute(t,e){return this.x=t.getX(e),this.y=t.getY(e),this.z=t.getZ(e),this.w=t.getW(e),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class Xm extends Br{constructor(t=1,e=1,n={}){super(),n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:Ie,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1,depth:1,multiview:!1},n),this.isRenderTarget=!0,this.width=t,this.height=e,this.depth=n.depth,this.scissor=new me(0,0,t,e),this.scissorTest=!1,this.viewport=new me(0,0,t,e),this.textures=[];const r={width:t,height:e,depth:n.depth},s=new Oe(r),a=n.count;for(let o=0;o<a;o++)this.textures[o]=s.clone(),this.textures[o].isRenderTargetTexture=!0,this.textures[o].renderTarget=this;this._setTextureOptions(n),this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this._depthTexture=null,this.depthTexture=n.depthTexture,this.samples=n.samples,this.multiview=n.multiview}_setTextureOptions(t={}){const e={minFilter:Ie,generateMipmaps:!1,flipY:!1,internalFormat:null};t.mapping!==void 0&&(e.mapping=t.mapping),t.wrapS!==void 0&&(e.wrapS=t.wrapS),t.wrapT!==void 0&&(e.wrapT=t.wrapT),t.wrapR!==void 0&&(e.wrapR=t.wrapR),t.magFilter!==void 0&&(e.magFilter=t.magFilter),t.minFilter!==void 0&&(e.minFilter=t.minFilter),t.format!==void 0&&(e.format=t.format),t.type!==void 0&&(e.type=t.type),t.anisotropy!==void 0&&(e.anisotropy=t.anisotropy),t.colorSpace!==void 0&&(e.colorSpace=t.colorSpace),t.flipY!==void 0&&(e.flipY=t.flipY),t.generateMipmaps!==void 0&&(e.generateMipmaps=t.generateMipmaps),t.internalFormat!==void 0&&(e.internalFormat=t.internalFormat);for(let n=0;n<this.textures.length;n++)this.textures[n].setValues(e)}get texture(){return this.textures[0]}set texture(t){this.textures[0]=t}set depthTexture(t){this._depthTexture!==null&&(this._depthTexture.renderTarget=null),t!==null&&(t.renderTarget=this),this._depthTexture=t}get depthTexture(){return this._depthTexture}setSize(t,e,n=1){if(this.width!==t||this.height!==e||this.depth!==n){this.width=t,this.height=e,this.depth=n;for(let r=0,s=this.textures.length;r<s;r++)this.textures[r].image.width=t,this.textures[r].image.height=e,this.textures[r].image.depth=n,this.textures[r].isData3DTexture!==!0&&(this.textures[r].isArrayTexture=this.textures[r].image.depth>1);this.dispose()}this.viewport.set(0,0,t,e),this.scissor.set(0,0,t,e)}clone(){return new this.constructor().copy(this)}copy(t){this.width=t.width,this.height=t.height,this.depth=t.depth,this.scissor.copy(t.scissor),this.scissorTest=t.scissorTest,this.viewport.copy(t.viewport),this.textures.length=0;for(let e=0,n=t.textures.length;e<n;e++){this.textures[e]=t.textures[e].clone(),this.textures[e].isRenderTargetTexture=!0,this.textures[e].renderTarget=this;const r=Object.assign({},t.textures[e].image);this.textures[e].source=new wc(r)}return this.depthBuffer=t.depthBuffer,this.stencilBuffer=t.stencilBuffer,this.resolveDepthBuffer=t.resolveDepthBuffer,this.resolveStencilBuffer=t.resolveStencilBuffer,t.depthTexture!==null&&(this.depthTexture=t.depthTexture.clone()),this.samples=t.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class Pn extends Xm{constructor(t=1,e=1,n={}){super(t,e,n),this.isWebGLRenderTarget=!0}}class Gh extends Oe{constructor(t=null,e=1,n=1,r=1){super(null),this.isDataArrayTexture=!0,this.image={data:t,width:e,height:n,depth:r},this.magFilter=we,this.minFilter=we,this.wrapR=Kn,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(t){this.layerUpdates.add(t)}clearLayerUpdates(){this.layerUpdates.clear()}}class qm extends Oe{constructor(t=null,e=1,n=1,r=1){super(null),this.isData3DTexture=!0,this.image={data:t,width:e,height:n,depth:r},this.magFilter=we,this.minFilter=we,this.wrapR=Kn,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class ve{constructor(t,e,n,r,s,a,o,l,c,u,h,f,d,_,g,p){ve.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],t!==void 0&&this.set(t,e,n,r,s,a,o,l,c,u,h,f,d,_,g,p)}set(t,e,n,r,s,a,o,l,c,u,h,f,d,_,g,p){const m=this.elements;return m[0]=t,m[4]=e,m[8]=n,m[12]=r,m[1]=s,m[5]=a,m[9]=o,m[13]=l,m[2]=c,m[6]=u,m[10]=h,m[14]=f,m[3]=d,m[7]=_,m[11]=g,m[15]=p,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new ve().fromArray(this.elements)}copy(t){const e=this.elements,n=t.elements;return e[0]=n[0],e[1]=n[1],e[2]=n[2],e[3]=n[3],e[4]=n[4],e[5]=n[5],e[6]=n[6],e[7]=n[7],e[8]=n[8],e[9]=n[9],e[10]=n[10],e[11]=n[11],e[12]=n[12],e[13]=n[13],e[14]=n[14],e[15]=n[15],this}copyPosition(t){const e=this.elements,n=t.elements;return e[12]=n[12],e[13]=n[13],e[14]=n[14],this}setFromMatrix3(t){const e=t.elements;return this.set(e[0],e[3],e[6],0,e[1],e[4],e[7],0,e[2],e[5],e[8],0,0,0,0,1),this}extractBasis(t,e,n){return this.determinant()===0?(t.set(1,0,0),e.set(0,1,0),n.set(0,0,1),this):(t.setFromMatrixColumn(this,0),e.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this)}makeBasis(t,e,n){return this.set(t.x,e.x,n.x,0,t.y,e.y,n.y,0,t.z,e.z,n.z,0,0,0,0,1),this}extractRotation(t){if(t.determinant()===0)return this.identity();const e=this.elements,n=t.elements,r=1/sr.setFromMatrixColumn(t,0).length(),s=1/sr.setFromMatrixColumn(t,1).length(),a=1/sr.setFromMatrixColumn(t,2).length();return e[0]=n[0]*r,e[1]=n[1]*r,e[2]=n[2]*r,e[3]=0,e[4]=n[4]*s,e[5]=n[5]*s,e[6]=n[6]*s,e[7]=0,e[8]=n[8]*a,e[9]=n[9]*a,e[10]=n[10]*a,e[11]=0,e[12]=0,e[13]=0,e[14]=0,e[15]=1,this}makeRotationFromEuler(t){const e=this.elements,n=t.x,r=t.y,s=t.z,a=Math.cos(n),o=Math.sin(n),l=Math.cos(r),c=Math.sin(r),u=Math.cos(s),h=Math.sin(s);if(t.order==="XYZ"){const f=a*u,d=a*h,_=o*u,g=o*h;e[0]=l*u,e[4]=-l*h,e[8]=c,e[1]=d+_*c,e[5]=f-g*c,e[9]=-o*l,e[2]=g-f*c,e[6]=_+d*c,e[10]=a*l}else if(t.order==="YXZ"){const f=l*u,d=l*h,_=c*u,g=c*h;e[0]=f+g*o,e[4]=_*o-d,e[8]=a*c,e[1]=a*h,e[5]=a*u,e[9]=-o,e[2]=d*o-_,e[6]=g+f*o,e[10]=a*l}else if(t.order==="ZXY"){const f=l*u,d=l*h,_=c*u,g=c*h;e[0]=f-g*o,e[4]=-a*h,e[8]=_+d*o,e[1]=d+_*o,e[5]=a*u,e[9]=g-f*o,e[2]=-a*c,e[6]=o,e[10]=a*l}else if(t.order==="ZYX"){const f=a*u,d=a*h,_=o*u,g=o*h;e[0]=l*u,e[4]=_*c-d,e[8]=f*c+g,e[1]=l*h,e[5]=g*c+f,e[9]=d*c-_,e[2]=-c,e[6]=o*l,e[10]=a*l}else if(t.order==="YZX"){const f=a*l,d=a*c,_=o*l,g=o*c;e[0]=l*u,e[4]=g-f*h,e[8]=_*h+d,e[1]=h,e[5]=a*u,e[9]=-o*u,e[2]=-c*u,e[6]=d*h+_,e[10]=f-g*h}else if(t.order==="XZY"){const f=a*l,d=a*c,_=o*l,g=o*c;e[0]=l*u,e[4]=-h,e[8]=c*u,e[1]=f*h+g,e[5]=a*u,e[9]=d*h-_,e[2]=_*h-d,e[6]=o*u,e[10]=g*h+f}return e[3]=0,e[7]=0,e[11]=0,e[12]=0,e[13]=0,e[14]=0,e[15]=1,this}makeRotationFromQuaternion(t){return this.compose(Ym,t,$m)}lookAt(t,e,n){const r=this.elements;return Ye.subVectors(t,e),Ye.lengthSq()===0&&(Ye.z=1),Ye.normalize(),li.crossVectors(n,Ye),li.lengthSq()===0&&(Math.abs(n.z)===1?Ye.x+=1e-4:Ye.z+=1e-4,Ye.normalize(),li.crossVectors(n,Ye)),li.normalize(),Ls.crossVectors(Ye,li),r[0]=li.x,r[4]=Ls.x,r[8]=Ye.x,r[1]=li.y,r[5]=Ls.y,r[9]=Ye.y,r[2]=li.z,r[6]=Ls.z,r[10]=Ye.z,this}multiply(t){return this.multiplyMatrices(this,t)}premultiply(t){return this.multiplyMatrices(t,this)}multiplyMatrices(t,e){const n=t.elements,r=e.elements,s=this.elements,a=n[0],o=n[4],l=n[8],c=n[12],u=n[1],h=n[5],f=n[9],d=n[13],_=n[2],g=n[6],p=n[10],m=n[14],M=n[3],T=n[7],S=n[11],b=n[15],A=r[0],R=r[4],x=r[8],y=r[12],G=r[1],D=r[5],B=r[9],k=r[13],X=r[2],C=r[6],L=r[10],P=r[14],z=r[3],O=r[7],J=r[11],Q=r[15];return s[0]=a*A+o*G+l*X+c*z,s[4]=a*R+o*D+l*C+c*O,s[8]=a*x+o*B+l*L+c*J,s[12]=a*y+o*k+l*P+c*Q,s[1]=u*A+h*G+f*X+d*z,s[5]=u*R+h*D+f*C+d*O,s[9]=u*x+h*B+f*L+d*J,s[13]=u*y+h*k+f*P+d*Q,s[2]=_*A+g*G+p*X+m*z,s[6]=_*R+g*D+p*C+m*O,s[10]=_*x+g*B+p*L+m*J,s[14]=_*y+g*k+p*P+m*Q,s[3]=M*A+T*G+S*X+b*z,s[7]=M*R+T*D+S*C+b*O,s[11]=M*x+T*B+S*L+b*J,s[15]=M*y+T*k+S*P+b*Q,this}multiplyScalar(t){const e=this.elements;return e[0]*=t,e[4]*=t,e[8]*=t,e[12]*=t,e[1]*=t,e[5]*=t,e[9]*=t,e[13]*=t,e[2]*=t,e[6]*=t,e[10]*=t,e[14]*=t,e[3]*=t,e[7]*=t,e[11]*=t,e[15]*=t,this}determinant(){const t=this.elements,e=t[0],n=t[4],r=t[8],s=t[12],a=t[1],o=t[5],l=t[9],c=t[13],u=t[2],h=t[6],f=t[10],d=t[14],_=t[3],g=t[7],p=t[11],m=t[15],M=l*d-c*f,T=o*d-c*h,S=o*f-l*h,b=a*d-c*u,A=a*f-l*u,R=a*h-o*u;return e*(g*M-p*T+m*S)-n*(_*M-p*b+m*A)+r*(_*T-g*b+m*R)-s*(_*S-g*A+p*R)}transpose(){const t=this.elements;let e;return e=t[1],t[1]=t[4],t[4]=e,e=t[2],t[2]=t[8],t[8]=e,e=t[6],t[6]=t[9],t[9]=e,e=t[3],t[3]=t[12],t[12]=e,e=t[7],t[7]=t[13],t[13]=e,e=t[11],t[11]=t[14],t[14]=e,this}setPosition(t,e,n){const r=this.elements;return t.isVector3?(r[12]=t.x,r[13]=t.y,r[14]=t.z):(r[12]=t,r[13]=e,r[14]=n),this}invert(){const t=this.elements,e=t[0],n=t[1],r=t[2],s=t[3],a=t[4],o=t[5],l=t[6],c=t[7],u=t[8],h=t[9],f=t[10],d=t[11],_=t[12],g=t[13],p=t[14],m=t[15],M=e*o-n*a,T=e*l-r*a,S=e*c-s*a,b=n*l-r*o,A=n*c-s*o,R=r*c-s*l,x=u*g-h*_,y=u*p-f*_,G=u*m-d*_,D=h*p-f*g,B=h*m-d*g,k=f*m-d*p,X=M*k-T*B+S*D+b*G-A*y+R*x;if(X===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const C=1/X;return t[0]=(o*k-l*B+c*D)*C,t[1]=(r*B-n*k-s*D)*C,t[2]=(g*R-p*A+m*b)*C,t[3]=(f*A-h*R-d*b)*C,t[4]=(l*G-a*k-c*y)*C,t[5]=(e*k-r*G+s*y)*C,t[6]=(p*S-_*R-m*T)*C,t[7]=(u*R-f*S+d*T)*C,t[8]=(a*B-o*G+c*x)*C,t[9]=(n*G-e*B-s*x)*C,t[10]=(_*A-g*S+m*M)*C,t[11]=(h*S-u*A-d*M)*C,t[12]=(o*y-a*D-l*x)*C,t[13]=(e*D-n*y+r*x)*C,t[14]=(g*T-_*b-p*M)*C,t[15]=(u*b-h*T+f*M)*C,this}scale(t){const e=this.elements,n=t.x,r=t.y,s=t.z;return e[0]*=n,e[4]*=r,e[8]*=s,e[1]*=n,e[5]*=r,e[9]*=s,e[2]*=n,e[6]*=r,e[10]*=s,e[3]*=n,e[7]*=r,e[11]*=s,this}getMaxScaleOnAxis(){const t=this.elements,e=t[0]*t[0]+t[1]*t[1]+t[2]*t[2],n=t[4]*t[4]+t[5]*t[5]+t[6]*t[6],r=t[8]*t[8]+t[9]*t[9]+t[10]*t[10];return Math.sqrt(Math.max(e,n,r))}makeTranslation(t,e,n){return t.isVector3?this.set(1,0,0,t.x,0,1,0,t.y,0,0,1,t.z,0,0,0,1):this.set(1,0,0,t,0,1,0,e,0,0,1,n,0,0,0,1),this}makeRotationX(t){const e=Math.cos(t),n=Math.sin(t);return this.set(1,0,0,0,0,e,-n,0,0,n,e,0,0,0,0,1),this}makeRotationY(t){const e=Math.cos(t),n=Math.sin(t);return this.set(e,0,n,0,0,1,0,0,-n,0,e,0,0,0,0,1),this}makeRotationZ(t){const e=Math.cos(t),n=Math.sin(t);return this.set(e,-n,0,0,n,e,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(t,e){const n=Math.cos(e),r=Math.sin(e),s=1-n,a=t.x,o=t.y,l=t.z,c=s*a,u=s*o;return this.set(c*a+n,c*o-r*l,c*l+r*o,0,c*o+r*l,u*o+n,u*l-r*a,0,c*l-r*o,u*l+r*a,s*l*l+n,0,0,0,0,1),this}makeScale(t,e,n){return this.set(t,0,0,0,0,e,0,0,0,0,n,0,0,0,0,1),this}makeShear(t,e,n,r,s,a){return this.set(1,n,s,0,t,1,a,0,e,r,1,0,0,0,0,1),this}compose(t,e,n){const r=this.elements,s=e._x,a=e._y,o=e._z,l=e._w,c=s+s,u=a+a,h=o+o,f=s*c,d=s*u,_=s*h,g=a*u,p=a*h,m=o*h,M=l*c,T=l*u,S=l*h,b=n.x,A=n.y,R=n.z;return r[0]=(1-(g+m))*b,r[1]=(d+S)*b,r[2]=(_-T)*b,r[3]=0,r[4]=(d-S)*A,r[5]=(1-(f+m))*A,r[6]=(p+M)*A,r[7]=0,r[8]=(_+T)*R,r[9]=(p-M)*R,r[10]=(1-(f+g))*R,r[11]=0,r[12]=t.x,r[13]=t.y,r[14]=t.z,r[15]=1,this}decompose(t,e,n){const r=this.elements;t.x=r[12],t.y=r[13],t.z=r[14];const s=this.determinant();if(s===0)return n.set(1,1,1),e.identity(),this;let a=sr.set(r[0],r[1],r[2]).length();const o=sr.set(r[4],r[5],r[6]).length(),l=sr.set(r[8],r[9],r[10]).length();s<0&&(a=-a),dn.copy(this);const c=1/a,u=1/o,h=1/l;return dn.elements[0]*=c,dn.elements[1]*=c,dn.elements[2]*=c,dn.elements[4]*=u,dn.elements[5]*=u,dn.elements[6]*=u,dn.elements[8]*=h,dn.elements[9]*=h,dn.elements[10]*=h,e.setFromRotationMatrix(dn),n.x=a,n.y=o,n.z=l,this}makePerspective(t,e,n,r,s,a,o=Rn,l=!1){const c=this.elements,u=2*s/(e-t),h=2*s/(n-r),f=(e+t)/(e-t),d=(n+r)/(n-r);let _,g;if(l)_=s/(a-s),g=a*s/(a-s);else if(o===Rn)_=-(a+s)/(a-s),g=-2*a*s/(a-s);else if(o===Ta)_=-a/(a-s),g=-a*s/(a-s);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+o);return c[0]=u,c[4]=0,c[8]=f,c[12]=0,c[1]=0,c[5]=h,c[9]=d,c[13]=0,c[2]=0,c[6]=0,c[10]=_,c[14]=g,c[3]=0,c[7]=0,c[11]=-1,c[15]=0,this}makeOrthographic(t,e,n,r,s,a,o=Rn,l=!1){const c=this.elements,u=2/(e-t),h=2/(n-r),f=-(e+t)/(e-t),d=-(n+r)/(n-r);let _,g;if(l)_=1/(a-s),g=a/(a-s);else if(o===Rn)_=-2/(a-s),g=-(a+s)/(a-s);else if(o===Ta)_=-1/(a-s),g=-s/(a-s);else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+o);return c[0]=u,c[4]=0,c[8]=0,c[12]=f,c[1]=0,c[5]=h,c[9]=0,c[13]=d,c[2]=0,c[6]=0,c[10]=_,c[14]=g,c[3]=0,c[7]=0,c[11]=0,c[15]=1,this}equals(t){const e=this.elements,n=t.elements;for(let r=0;r<16;r++)if(e[r]!==n[r])return!1;return!0}fromArray(t,e=0){for(let n=0;n<16;n++)this.elements[n]=t[n+e];return this}toArray(t=[],e=0){const n=this.elements;return t[e]=n[0],t[e+1]=n[1],t[e+2]=n[2],t[e+3]=n[3],t[e+4]=n[4],t[e+5]=n[5],t[e+6]=n[6],t[e+7]=n[7],t[e+8]=n[8],t[e+9]=n[9],t[e+10]=n[10],t[e+11]=n[11],t[e+12]=n[12],t[e+13]=n[13],t[e+14]=n[14],t[e+15]=n[15],t}}const sr=new W,dn=new ve,Ym=new W(0,0,0),$m=new W(1,1,1),li=new W,Ls=new W,Ye=new W,Su=new ve,yu=new kr;class ii{constructor(t=0,e=0,n=0,r=ii.DEFAULT_ORDER){this.isEuler=!0,this._x=t,this._y=e,this._z=n,this._order=r}get x(){return this._x}set x(t){this._x=t,this._onChangeCallback()}get y(){return this._y}set y(t){this._y=t,this._onChangeCallback()}get z(){return this._z}set z(t){this._z=t,this._onChangeCallback()}get order(){return this._order}set order(t){this._order=t,this._onChangeCallback()}set(t,e,n,r=this._order){return this._x=t,this._y=e,this._z=n,this._order=r,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(t){return this._x=t._x,this._y=t._y,this._z=t._z,this._order=t._order,this._onChangeCallback(),this}setFromRotationMatrix(t,e=this._order,n=!0){const r=t.elements,s=r[0],a=r[4],o=r[8],l=r[1],c=r[5],u=r[9],h=r[2],f=r[6],d=r[10];switch(e){case"XYZ":this._y=Math.asin(zt(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(-u,d),this._z=Math.atan2(-a,s)):(this._x=Math.atan2(f,c),this._z=0);break;case"YXZ":this._x=Math.asin(-zt(u,-1,1)),Math.abs(u)<.9999999?(this._y=Math.atan2(o,d),this._z=Math.atan2(l,c)):(this._y=Math.atan2(-h,s),this._z=0);break;case"ZXY":this._x=Math.asin(zt(f,-1,1)),Math.abs(f)<.9999999?(this._y=Math.atan2(-h,d),this._z=Math.atan2(-a,c)):(this._y=0,this._z=Math.atan2(l,s));break;case"ZYX":this._y=Math.asin(-zt(h,-1,1)),Math.abs(h)<.9999999?(this._x=Math.atan2(f,d),this._z=Math.atan2(l,s)):(this._x=0,this._z=Math.atan2(-a,c));break;case"YZX":this._z=Math.asin(zt(l,-1,1)),Math.abs(l)<.9999999?(this._x=Math.atan2(-u,c),this._y=Math.atan2(-h,s)):(this._x=0,this._y=Math.atan2(o,d));break;case"XZY":this._z=Math.asin(-zt(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(f,c),this._y=Math.atan2(o,s)):(this._x=Math.atan2(-u,d),this._y=0);break;default:Pt("Euler: .setFromRotationMatrix() encountered an unknown order: "+e)}return this._order=e,n===!0&&this._onChangeCallback(),this}setFromQuaternion(t,e,n){return Su.makeRotationFromQuaternion(t),this.setFromRotationMatrix(Su,e,n)}setFromVector3(t,e=this._order){return this.set(t.x,t.y,t.z,e)}reorder(t){return yu.setFromEuler(this),this.setFromQuaternion(yu,t)}equals(t){return t._x===this._x&&t._y===this._y&&t._z===this._z&&t._order===this._order}fromArray(t){return this._x=t[0],this._y=t[1],this._z=t[2],t[3]!==void 0&&(this._order=t[3]),this._onChangeCallback(),this}toArray(t=[],e=0){return t[e]=this._x,t[e+1]=this._y,t[e+2]=this._z,t[e+3]=this._order,t}_onChange(t){return this._onChangeCallback=t,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}ii.DEFAULT_ORDER="XYZ";class Hh{constructor(){this.mask=1}set(t){this.mask=(1<<t|0)>>>0}enable(t){this.mask|=1<<t|0}enableAll(){this.mask=-1}toggle(t){this.mask^=1<<t|0}disable(t){this.mask&=~(1<<t|0)}disableAll(){this.mask=0}test(t){return(this.mask&t.mask)!==0}isEnabled(t){return(this.mask&(1<<t|0))!==0}}let Km=0;const Eu=new W,ar=new kr,zn=new ve,Is=new W,Hr=new W,Zm=new W,Jm=new kr,Tu=new W(1,0,0),bu=new W(0,1,0),Au=new W(0,0,1),wu={type:"added"},jm={type:"removed"},or={type:"childadded",child:null},co={type:"childremoved",child:null};class tn extends Br{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:Km++}),this.uuid=ys(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=tn.DEFAULT_UP.clone();const t=new W,e=new ii,n=new kr,r=new W(1,1,1);function s(){n.setFromEuler(e,!1)}function a(){e.setFromQuaternion(n,void 0,!1)}e._onChange(s),n._onChange(a),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:t},rotation:{configurable:!0,enumerable:!0,value:e},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:r},modelViewMatrix:{value:new ve},normalMatrix:{value:new It}}),this.matrix=new ve,this.matrixWorld=new ve,this.matrixAutoUpdate=tn.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=tn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new Hh,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.customDepthMaterial=void 0,this.customDistanceMaterial=void 0,this.static=!1,this.userData={},this.pivot=null}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(t){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(t),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(t){return this.quaternion.premultiply(t),this}setRotationFromAxisAngle(t,e){this.quaternion.setFromAxisAngle(t,e)}setRotationFromEuler(t){this.quaternion.setFromEuler(t,!0)}setRotationFromMatrix(t){this.quaternion.setFromRotationMatrix(t)}setRotationFromQuaternion(t){this.quaternion.copy(t)}rotateOnAxis(t,e){return ar.setFromAxisAngle(t,e),this.quaternion.multiply(ar),this}rotateOnWorldAxis(t,e){return ar.setFromAxisAngle(t,e),this.quaternion.premultiply(ar),this}rotateX(t){return this.rotateOnAxis(Tu,t)}rotateY(t){return this.rotateOnAxis(bu,t)}rotateZ(t){return this.rotateOnAxis(Au,t)}translateOnAxis(t,e){return Eu.copy(t).applyQuaternion(this.quaternion),this.position.add(Eu.multiplyScalar(e)),this}translateX(t){return this.translateOnAxis(Tu,t)}translateY(t){return this.translateOnAxis(bu,t)}translateZ(t){return this.translateOnAxis(Au,t)}localToWorld(t){return this.updateWorldMatrix(!0,!1),t.applyMatrix4(this.matrixWorld)}worldToLocal(t){return this.updateWorldMatrix(!0,!1),t.applyMatrix4(zn.copy(this.matrixWorld).invert())}lookAt(t,e,n){t.isVector3?Is.copy(t):Is.set(t,e,n);const r=this.parent;this.updateWorldMatrix(!0,!1),Hr.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?zn.lookAt(Hr,Is,this.up):zn.lookAt(Is,Hr,this.up),this.quaternion.setFromRotationMatrix(zn),r&&(zn.extractRotation(r.matrixWorld),ar.setFromRotationMatrix(zn),this.quaternion.premultiply(ar.invert()))}add(t){if(arguments.length>1){for(let e=0;e<arguments.length;e++)this.add(arguments[e]);return this}return t===this?(Xt("Object3D.add: object can't be added as a child of itself.",t),this):(t&&t.isObject3D?(t.removeFromParent(),t.parent=this,this.children.push(t),t.dispatchEvent(wu),or.child=t,this.dispatchEvent(or),or.child=null):Xt("Object3D.add: object not an instance of THREE.Object3D.",t),this)}remove(t){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const e=this.children.indexOf(t);return e!==-1&&(t.parent=null,this.children.splice(e,1),t.dispatchEvent(jm),co.child=t,this.dispatchEvent(co),co.child=null),this}removeFromParent(){const t=this.parent;return t!==null&&t.remove(this),this}clear(){return this.remove(...this.children)}attach(t){return this.updateWorldMatrix(!0,!1),zn.copy(this.matrixWorld).invert(),t.parent!==null&&(t.parent.updateWorldMatrix(!0,!1),zn.multiply(t.parent.matrixWorld)),t.applyMatrix4(zn),t.removeFromParent(),t.parent=this,this.children.push(t),t.updateWorldMatrix(!1,!0),t.dispatchEvent(wu),or.child=t,this.dispatchEvent(or),or.child=null,this}getObjectById(t){return this.getObjectByProperty("id",t)}getObjectByName(t){return this.getObjectByProperty("name",t)}getObjectByProperty(t,e){if(this[t]===e)return this;for(let n=0,r=this.children.length;n<r;n++){const a=this.children[n].getObjectByProperty(t,e);if(a!==void 0)return a}}getObjectsByProperty(t,e,n=[]){this[t]===e&&n.push(this);const r=this.children;for(let s=0,a=r.length;s<a;s++)r[s].getObjectsByProperty(t,e,n);return n}getWorldPosition(t){return this.updateWorldMatrix(!0,!1),t.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(t){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Hr,t,Zm),t}getWorldScale(t){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Hr,Jm,t),t}getWorldDirection(t){this.updateWorldMatrix(!0,!1);const e=this.matrixWorld.elements;return t.set(e[8],e[9],e[10]).normalize()}raycast(){}traverse(t){t(this);const e=this.children;for(let n=0,r=e.length;n<r;n++)e[n].traverse(t)}traverseVisible(t){if(this.visible===!1)return;t(this);const e=this.children;for(let n=0,r=e.length;n<r;n++)e[n].traverseVisible(t)}traverseAncestors(t){const e=this.parent;e!==null&&(t(e),e.traverseAncestors(t))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale);const t=this.pivot;if(t!==null){const e=t.x,n=t.y,r=t.z,s=this.matrix.elements;s[12]+=e-s[0]*e-s[4]*n-s[8]*r,s[13]+=n-s[1]*e-s[5]*n-s[9]*r,s[14]+=r-s[2]*e-s[6]*n-s[10]*r}this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(t){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||t)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,t=!0);const e=this.children;for(let n=0,r=e.length;n<r;n++)e[n].updateMatrixWorld(t)}updateWorldMatrix(t,e){const n=this.parent;if(t===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),e===!0){const r=this.children;for(let s=0,a=r.length;s<a;s++)r[s].updateWorldMatrix(!1,!0)}}toJSON(t){const e=t===void 0||typeof t=="string",n={};e&&(t={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.7,type:"Object",generator:"Object3D.toJSON"});const r={};r.uuid=this.uuid,r.type=this.type,this.name!==""&&(r.name=this.name),this.castShadow===!0&&(r.castShadow=!0),this.receiveShadow===!0&&(r.receiveShadow=!0),this.visible===!1&&(r.visible=!1),this.frustumCulled===!1&&(r.frustumCulled=!1),this.renderOrder!==0&&(r.renderOrder=this.renderOrder),this.static!==!1&&(r.static=this.static),Object.keys(this.userData).length>0&&(r.userData=this.userData),r.layers=this.layers.mask,r.matrix=this.matrix.toArray(),r.up=this.up.toArray(),this.pivot!==null&&(r.pivot=this.pivot.toArray()),this.matrixAutoUpdate===!1&&(r.matrixAutoUpdate=!1),this.morphTargetDictionary!==void 0&&(r.morphTargetDictionary=Object.assign({},this.morphTargetDictionary)),this.morphTargetInfluences!==void 0&&(r.morphTargetInfluences=this.morphTargetInfluences.slice()),this.isInstancedMesh&&(r.type="InstancedMesh",r.count=this.count,r.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(r.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(r.type="BatchedMesh",r.perObjectFrustumCulled=this.perObjectFrustumCulled,r.sortObjects=this.sortObjects,r.drawRanges=this._drawRanges,r.reservedRanges=this._reservedRanges,r.geometryInfo=this._geometryInfo.map(o=>({...o,boundingBox:o.boundingBox?o.boundingBox.toJSON():void 0,boundingSphere:o.boundingSphere?o.boundingSphere.toJSON():void 0})),r.instanceInfo=this._instanceInfo.map(o=>({...o})),r.availableInstanceIds=this._availableInstanceIds.slice(),r.availableGeometryIds=this._availableGeometryIds.slice(),r.nextIndexStart=this._nextIndexStart,r.nextVertexStart=this._nextVertexStart,r.geometryCount=this._geometryCount,r.maxInstanceCount=this._maxInstanceCount,r.maxVertexCount=this._maxVertexCount,r.maxIndexCount=this._maxIndexCount,r.geometryInitialized=this._geometryInitialized,r.matricesTexture=this._matricesTexture.toJSON(t),r.indirectTexture=this._indirectTexture.toJSON(t),this._colorsTexture!==null&&(r.colorsTexture=this._colorsTexture.toJSON(t)),this.boundingSphere!==null&&(r.boundingSphere=this.boundingSphere.toJSON()),this.boundingBox!==null&&(r.boundingBox=this.boundingBox.toJSON()));function s(o,l){return o[l.uuid]===void 0&&(o[l.uuid]=l.toJSON(t)),l.uuid}if(this.isScene)this.background&&(this.background.isColor?r.background=this.background.toJSON():this.background.isTexture&&(r.background=this.background.toJSON(t).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(r.environment=this.environment.toJSON(t).uuid);else if(this.isMesh||this.isLine||this.isPoints){r.geometry=s(t.geometries,this.geometry);const o=this.geometry.parameters;if(o!==void 0&&o.shapes!==void 0){const l=o.shapes;if(Array.isArray(l))for(let c=0,u=l.length;c<u;c++){const h=l[c];s(t.shapes,h)}else s(t.shapes,l)}}if(this.isSkinnedMesh&&(r.bindMode=this.bindMode,r.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(s(t.skeletons,this.skeleton),r.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const o=[];for(let l=0,c=this.material.length;l<c;l++)o.push(s(t.materials,this.material[l]));r.material=o}else r.material=s(t.materials,this.material);if(this.children.length>0){r.children=[];for(let o=0;o<this.children.length;o++)r.children.push(this.children[o].toJSON(t).object)}if(this.animations.length>0){r.animations=[];for(let o=0;o<this.animations.length;o++){const l=this.animations[o];r.animations.push(s(t.animations,l))}}if(e){const o=a(t.geometries),l=a(t.materials),c=a(t.textures),u=a(t.images),h=a(t.shapes),f=a(t.skeletons),d=a(t.animations),_=a(t.nodes);o.length>0&&(n.geometries=o),l.length>0&&(n.materials=l),c.length>0&&(n.textures=c),u.length>0&&(n.images=u),h.length>0&&(n.shapes=h),f.length>0&&(n.skeletons=f),d.length>0&&(n.animations=d),_.length>0&&(n.nodes=_)}return n.object=r,n;function a(o){const l=[];for(const c in o){const u=o[c];delete u.metadata,l.push(u)}return l}}clone(t){return new this.constructor().copy(this,t)}copy(t,e=!0){if(this.name=t.name,this.up.copy(t.up),this.position.copy(t.position),this.rotation.order=t.rotation.order,this.quaternion.copy(t.quaternion),this.scale.copy(t.scale),t.pivot!==null&&(this.pivot=t.pivot.clone()),this.matrix.copy(t.matrix),this.matrixWorld.copy(t.matrixWorld),this.matrixAutoUpdate=t.matrixAutoUpdate,this.matrixWorldAutoUpdate=t.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=t.matrixWorldNeedsUpdate,this.layers.mask=t.layers.mask,this.visible=t.visible,this.castShadow=t.castShadow,this.receiveShadow=t.receiveShadow,this.frustumCulled=t.frustumCulled,this.renderOrder=t.renderOrder,this.static=t.static,this.animations=t.animations.slice(),this.userData=JSON.parse(JSON.stringify(t.userData)),e===!0)for(let n=0;n<t.children.length;n++){const r=t.children[n];this.add(r.clone())}return this}}tn.DEFAULT_UP=new W(0,1,0);tn.DEFAULT_MATRIX_AUTO_UPDATE=!0;tn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;class Us extends tn{constructor(){super(),this.isGroup=!0,this.type="Group"}}const Qm={type:"move"};class uo{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new Us,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new Us,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new W,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new W),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new Us,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new W,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new W),this._grip}dispatchEvent(t){return this._targetRay!==null&&this._targetRay.dispatchEvent(t),this._grip!==null&&this._grip.dispatchEvent(t),this._hand!==null&&this._hand.dispatchEvent(t),this}connect(t){if(t&&t.hand){const e=this._hand;if(e)for(const n of t.hand.values())this._getHandJoint(e,n)}return this.dispatchEvent({type:"connected",data:t}),this}disconnect(t){return this.dispatchEvent({type:"disconnected",data:t}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(t,e,n){let r=null,s=null,a=null;const o=this._targetRay,l=this._grip,c=this._hand;if(t&&e.session.visibilityState!=="visible-blurred"){if(c&&t.hand){a=!0;for(const g of t.hand.values()){const p=e.getJointPose(g,n),m=this._getHandJoint(c,g);p!==null&&(m.matrix.fromArray(p.transform.matrix),m.matrix.decompose(m.position,m.rotation,m.scale),m.matrixWorldNeedsUpdate=!0,m.jointRadius=p.radius),m.visible=p!==null}const u=c.joints["index-finger-tip"],h=c.joints["thumb-tip"],f=u.position.distanceTo(h.position),d=.02,_=.005;c.inputState.pinching&&f>d+_?(c.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:t.handedness,target:this})):!c.inputState.pinching&&f<=d-_&&(c.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:t.handedness,target:this}))}else l!==null&&t.gripSpace&&(s=e.getPose(t.gripSpace,n),s!==null&&(l.matrix.fromArray(s.transform.matrix),l.matrix.decompose(l.position,l.rotation,l.scale),l.matrixWorldNeedsUpdate=!0,s.linearVelocity?(l.hasLinearVelocity=!0,l.linearVelocity.copy(s.linearVelocity)):l.hasLinearVelocity=!1,s.angularVelocity?(l.hasAngularVelocity=!0,l.angularVelocity.copy(s.angularVelocity)):l.hasAngularVelocity=!1));o!==null&&(r=e.getPose(t.targetRaySpace,n),r===null&&s!==null&&(r=s),r!==null&&(o.matrix.fromArray(r.transform.matrix),o.matrix.decompose(o.position,o.rotation,o.scale),o.matrixWorldNeedsUpdate=!0,r.linearVelocity?(o.hasLinearVelocity=!0,o.linearVelocity.copy(r.linearVelocity)):o.hasLinearVelocity=!1,r.angularVelocity?(o.hasAngularVelocity=!0,o.angularVelocity.copy(r.angularVelocity)):o.hasAngularVelocity=!1,this.dispatchEvent(Qm)))}return o!==null&&(o.visible=r!==null),l!==null&&(l.visible=s!==null),c!==null&&(c.visible=a!==null),this}_getHandJoint(t,e){if(t.joints[e.jointName]===void 0){const n=new Us;n.matrixAutoUpdate=!1,n.visible=!1,t.joints[e.jointName]=n,t.add(n)}return t.joints[e.jointName]}}const Wh={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},ci={h:0,s:0,l:0},Ns={h:0,s:0,l:0};function fo(i,t,e){return e<0&&(e+=1),e>1&&(e-=1),e<1/6?i+(t-i)*6*e:e<1/2?t:e<2/3?i+(t-i)*6*(2/3-e):i}let Zt=class{constructor(t,e,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(t,e,n)}set(t,e,n){if(e===void 0&&n===void 0){const r=t;r&&r.isColor?this.copy(r):typeof r=="number"?this.setHex(r):typeof r=="string"&&this.setStyle(r)}else this.setRGB(t,e,n);return this}setScalar(t){return this.r=t,this.g=t,this.b=t,this}setHex(t,e=on){return t=Math.floor(t),this.r=(t>>16&255)/255,this.g=(t>>8&255)/255,this.b=(t&255)/255,Ht.colorSpaceToWorking(this,e),this}setRGB(t,e,n,r=Ht.workingColorSpace){return this.r=t,this.g=e,this.b=n,Ht.colorSpaceToWorking(this,r),this}setHSL(t,e,n,r=Ht.workingColorSpace){if(t=zm(t,1),e=zt(e,0,1),n=zt(n,0,1),e===0)this.r=this.g=this.b=n;else{const s=n<=.5?n*(1+e):n+e-n*e,a=2*n-s;this.r=fo(a,s,t+1/3),this.g=fo(a,s,t),this.b=fo(a,s,t-1/3)}return Ht.colorSpaceToWorking(this,r),this}setStyle(t,e=on){function n(s){s!==void 0&&parseFloat(s)<1&&Pt("Color: Alpha component of "+t+" will be ignored.")}let r;if(r=/^(\w+)\(([^\)]*)\)/.exec(t)){let s;const a=r[1],o=r[2];switch(a){case"rgb":case"rgba":if(s=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(s[4]),this.setRGB(Math.min(255,parseInt(s[1],10))/255,Math.min(255,parseInt(s[2],10))/255,Math.min(255,parseInt(s[3],10))/255,e);if(s=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(s[4]),this.setRGB(Math.min(100,parseInt(s[1],10))/100,Math.min(100,parseInt(s[2],10))/100,Math.min(100,parseInt(s[3],10))/100,e);break;case"hsl":case"hsla":if(s=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(o))return n(s[4]),this.setHSL(parseFloat(s[1])/360,parseFloat(s[2])/100,parseFloat(s[3])/100,e);break;default:Pt("Color: Unknown color model "+t)}}else if(r=/^\#([A-Fa-f\d]+)$/.exec(t)){const s=r[1],a=s.length;if(a===3)return this.setRGB(parseInt(s.charAt(0),16)/15,parseInt(s.charAt(1),16)/15,parseInt(s.charAt(2),16)/15,e);if(a===6)return this.setHex(parseInt(s,16),e);Pt("Color: Invalid hex color "+t)}else if(t&&t.length>0)return this.setColorName(t,e);return this}setColorName(t,e=on){const n=Wh[t.toLowerCase()];return n!==void 0?this.setHex(n,e):Pt("Color: Unknown color "+t),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(t){return this.r=t.r,this.g=t.g,this.b=t.b,this}copySRGBToLinear(t){return this.r=Jn(t.r),this.g=Jn(t.g),this.b=Jn(t.b),this}copyLinearToSRGB(t){return this.r=Er(t.r),this.g=Er(t.g),this.b=Er(t.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(t=on){return Ht.workingToColorSpace(De.copy(this),t),Math.round(zt(De.r*255,0,255))*65536+Math.round(zt(De.g*255,0,255))*256+Math.round(zt(De.b*255,0,255))}getHexString(t=on){return("000000"+this.getHex(t).toString(16)).slice(-6)}getHSL(t,e=Ht.workingColorSpace){Ht.workingToColorSpace(De.copy(this),e);const n=De.r,r=De.g,s=De.b,a=Math.max(n,r,s),o=Math.min(n,r,s);let l,c;const u=(o+a)/2;if(o===a)l=0,c=0;else{const h=a-o;switch(c=u<=.5?h/(a+o):h/(2-a-o),a){case n:l=(r-s)/h+(r<s?6:0);break;case r:l=(s-n)/h+2;break;case s:l=(n-r)/h+4;break}l/=6}return t.h=l,t.s=c,t.l=u,t}getRGB(t,e=Ht.workingColorSpace){return Ht.workingToColorSpace(De.copy(this),e),t.r=De.r,t.g=De.g,t.b=De.b,t}getStyle(t=on){Ht.workingToColorSpace(De.copy(this),t);const e=De.r,n=De.g,r=De.b;return t!==on?`color(${t} ${e.toFixed(3)} ${n.toFixed(3)} ${r.toFixed(3)})`:`rgb(${Math.round(e*255)},${Math.round(n*255)},${Math.round(r*255)})`}offsetHSL(t,e,n){return this.getHSL(ci),this.setHSL(ci.h+t,ci.s+e,ci.l+n)}add(t){return this.r+=t.r,this.g+=t.g,this.b+=t.b,this}addColors(t,e){return this.r=t.r+e.r,this.g=t.g+e.g,this.b=t.b+e.b,this}addScalar(t){return this.r+=t,this.g+=t,this.b+=t,this}sub(t){return this.r=Math.max(0,this.r-t.r),this.g=Math.max(0,this.g-t.g),this.b=Math.max(0,this.b-t.b),this}multiply(t){return this.r*=t.r,this.g*=t.g,this.b*=t.b,this}multiplyScalar(t){return this.r*=t,this.g*=t,this.b*=t,this}lerp(t,e){return this.r+=(t.r-this.r)*e,this.g+=(t.g-this.g)*e,this.b+=(t.b-this.b)*e,this}lerpColors(t,e,n){return this.r=t.r+(e.r-t.r)*n,this.g=t.g+(e.g-t.g)*n,this.b=t.b+(e.b-t.b)*n,this}lerpHSL(t,e){this.getHSL(ci),t.getHSL(Ns);const n=ro(ci.h,Ns.h,e),r=ro(ci.s,Ns.s,e),s=ro(ci.l,Ns.l,e);return this.setHSL(n,r,s),this}setFromVector3(t){return this.r=t.x,this.g=t.y,this.b=t.z,this}applyMatrix3(t){const e=this.r,n=this.g,r=this.b,s=t.elements;return this.r=s[0]*e+s[3]*n+s[6]*r,this.g=s[1]*e+s[4]*n+s[7]*r,this.b=s[2]*e+s[5]*n+s[8]*r,this}equals(t){return t.r===this.r&&t.g===this.g&&t.b===this.b}fromArray(t,e=0){return this.r=t[e],this.g=t[e+1],this.b=t[e+2],this}toArray(t=[],e=0){return t[e]=this.r,t[e+1]=this.g,t[e+2]=this.b,t}fromBufferAttribute(t,e){return this.r=t.getX(e),this.g=t.getY(e),this.b=t.getZ(e),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}};const De=new Zt;Zt.NAMES=Wh;class t_ extends tn{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new ii,this.environmentIntensity=1,this.environmentRotation=new ii,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(t,e){return super.copy(t,e),t.background!==null&&(this.background=t.background.clone()),t.environment!==null&&(this.environment=t.environment.clone()),t.fog!==null&&(this.fog=t.fog.clone()),this.backgroundBlurriness=t.backgroundBlurriness,this.backgroundIntensity=t.backgroundIntensity,this.backgroundRotation.copy(t.backgroundRotation),this.environmentIntensity=t.environmentIntensity,this.environmentRotation.copy(t.environmentRotation),t.overrideMaterial!==null&&(this.overrideMaterial=t.overrideMaterial.clone()),this.matrixAutoUpdate=t.matrixAutoUpdate,this}toJSON(t){const e=super.toJSON(t);return this.fog!==null&&(e.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(e.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(e.object.backgroundIntensity=this.backgroundIntensity),e.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(e.object.environmentIntensity=this.environmentIntensity),e.object.environmentRotation=this.environmentRotation.toArray(),e}}const pn=new W,Vn=new W,ho=new W,Gn=new W,lr=new W,cr=new W,Ru=new W,po=new W,mo=new W,_o=new W,go=new me,xo=new me,vo=new me;class _n{constructor(t=new W,e=new W,n=new W){this.a=t,this.b=e,this.c=n}static getNormal(t,e,n,r){r.subVectors(n,e),pn.subVectors(t,e),r.cross(pn);const s=r.lengthSq();return s>0?r.multiplyScalar(1/Math.sqrt(s)):r.set(0,0,0)}static getBarycoord(t,e,n,r,s){pn.subVectors(r,e),Vn.subVectors(n,e),ho.subVectors(t,e);const a=pn.dot(pn),o=pn.dot(Vn),l=pn.dot(ho),c=Vn.dot(Vn),u=Vn.dot(ho),h=a*c-o*o;if(h===0)return s.set(0,0,0),null;const f=1/h,d=(c*l-o*u)*f,_=(a*u-o*l)*f;return s.set(1-d-_,_,d)}static containsPoint(t,e,n,r){return this.getBarycoord(t,e,n,r,Gn)===null?!1:Gn.x>=0&&Gn.y>=0&&Gn.x+Gn.y<=1}static getInterpolation(t,e,n,r,s,a,o,l){return this.getBarycoord(t,e,n,r,Gn)===null?(l.x=0,l.y=0,"z"in l&&(l.z=0),"w"in l&&(l.w=0),null):(l.setScalar(0),l.addScaledVector(s,Gn.x),l.addScaledVector(a,Gn.y),l.addScaledVector(o,Gn.z),l)}static getInterpolatedAttribute(t,e,n,r,s,a){return go.setScalar(0),xo.setScalar(0),vo.setScalar(0),go.fromBufferAttribute(t,e),xo.fromBufferAttribute(t,n),vo.fromBufferAttribute(t,r),a.setScalar(0),a.addScaledVector(go,s.x),a.addScaledVector(xo,s.y),a.addScaledVector(vo,s.z),a}static isFrontFacing(t,e,n,r){return pn.subVectors(n,e),Vn.subVectors(t,e),pn.cross(Vn).dot(r)<0}set(t,e,n){return this.a.copy(t),this.b.copy(e),this.c.copy(n),this}setFromPointsAndIndices(t,e,n,r){return this.a.copy(t[e]),this.b.copy(t[n]),this.c.copy(t[r]),this}setFromAttributeAndIndices(t,e,n,r){return this.a.fromBufferAttribute(t,e),this.b.fromBufferAttribute(t,n),this.c.fromBufferAttribute(t,r),this}clone(){return new this.constructor().copy(this)}copy(t){return this.a.copy(t.a),this.b.copy(t.b),this.c.copy(t.c),this}getArea(){return pn.subVectors(this.c,this.b),Vn.subVectors(this.a,this.b),pn.cross(Vn).length()*.5}getMidpoint(t){return t.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(t){return _n.getNormal(this.a,this.b,this.c,t)}getPlane(t){return t.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(t,e){return _n.getBarycoord(t,this.a,this.b,this.c,e)}getInterpolation(t,e,n,r,s){return _n.getInterpolation(t,this.a,this.b,this.c,e,n,r,s)}containsPoint(t){return _n.containsPoint(t,this.a,this.b,this.c)}isFrontFacing(t){return _n.isFrontFacing(this.a,this.b,this.c,t)}intersectsBox(t){return t.intersectsTriangle(this)}closestPointToPoint(t,e){const n=this.a,r=this.b,s=this.c;let a,o;lr.subVectors(r,n),cr.subVectors(s,n),po.subVectors(t,n);const l=lr.dot(po),c=cr.dot(po);if(l<=0&&c<=0)return e.copy(n);mo.subVectors(t,r);const u=lr.dot(mo),h=cr.dot(mo);if(u>=0&&h<=u)return e.copy(r);const f=l*h-u*c;if(f<=0&&l>=0&&u<=0)return a=l/(l-u),e.copy(n).addScaledVector(lr,a);_o.subVectors(t,s);const d=lr.dot(_o),_=cr.dot(_o);if(_>=0&&d<=_)return e.copy(s);const g=d*c-l*_;if(g<=0&&c>=0&&_<=0)return o=c/(c-_),e.copy(n).addScaledVector(cr,o);const p=u*_-d*h;if(p<=0&&h-u>=0&&d-_>=0)return Ru.subVectors(s,r),o=(h-u)/(h-u+(d-_)),e.copy(r).addScaledVector(Ru,o);const m=1/(p+g+f);return a=g*m,o=f*m,e.copy(n).addScaledVector(lr,a).addScaledVector(cr,o)}equals(t){return t.a.equals(this.a)&&t.b.equals(this.b)&&t.c.equals(this.c)}}class Es{constructor(t=new W(1/0,1/0,1/0),e=new W(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=t,this.max=e}set(t,e){return this.min.copy(t),this.max.copy(e),this}setFromArray(t){this.makeEmpty();for(let e=0,n=t.length;e<n;e+=3)this.expandByPoint(mn.fromArray(t,e));return this}setFromBufferAttribute(t){this.makeEmpty();for(let e=0,n=t.count;e<n;e++)this.expandByPoint(mn.fromBufferAttribute(t,e));return this}setFromPoints(t){this.makeEmpty();for(let e=0,n=t.length;e<n;e++)this.expandByPoint(t[e]);return this}setFromCenterAndSize(t,e){const n=mn.copy(e).multiplyScalar(.5);return this.min.copy(t).sub(n),this.max.copy(t).add(n),this}setFromObject(t,e=!1){return this.makeEmpty(),this.expandByObject(t,e)}clone(){return new this.constructor().copy(this)}copy(t){return this.min.copy(t.min),this.max.copy(t.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(t){return this.isEmpty()?t.set(0,0,0):t.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(t){return this.isEmpty()?t.set(0,0,0):t.subVectors(this.max,this.min)}expandByPoint(t){return this.min.min(t),this.max.max(t),this}expandByVector(t){return this.min.sub(t),this.max.add(t),this}expandByScalar(t){return this.min.addScalar(-t),this.max.addScalar(t),this}expandByObject(t,e=!1){t.updateWorldMatrix(!1,!1);const n=t.geometry;if(n!==void 0){const s=n.getAttribute("position");if(e===!0&&s!==void 0&&t.isInstancedMesh!==!0)for(let a=0,o=s.count;a<o;a++)t.isMesh===!0?t.getVertexPosition(a,mn):mn.fromBufferAttribute(s,a),mn.applyMatrix4(t.matrixWorld),this.expandByPoint(mn);else t.boundingBox!==void 0?(t.boundingBox===null&&t.computeBoundingBox(),Fs.copy(t.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),Fs.copy(n.boundingBox)),Fs.applyMatrix4(t.matrixWorld),this.union(Fs)}const r=t.children;for(let s=0,a=r.length;s<a;s++)this.expandByObject(r[s],e);return this}containsPoint(t){return t.x>=this.min.x&&t.x<=this.max.x&&t.y>=this.min.y&&t.y<=this.max.y&&t.z>=this.min.z&&t.z<=this.max.z}containsBox(t){return this.min.x<=t.min.x&&t.max.x<=this.max.x&&this.min.y<=t.min.y&&t.max.y<=this.max.y&&this.min.z<=t.min.z&&t.max.z<=this.max.z}getParameter(t,e){return e.set((t.x-this.min.x)/(this.max.x-this.min.x),(t.y-this.min.y)/(this.max.y-this.min.y),(t.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(t){return t.max.x>=this.min.x&&t.min.x<=this.max.x&&t.max.y>=this.min.y&&t.min.y<=this.max.y&&t.max.z>=this.min.z&&t.min.z<=this.max.z}intersectsSphere(t){return this.clampPoint(t.center,mn),mn.distanceToSquared(t.center)<=t.radius*t.radius}intersectsPlane(t){let e,n;return t.normal.x>0?(e=t.normal.x*this.min.x,n=t.normal.x*this.max.x):(e=t.normal.x*this.max.x,n=t.normal.x*this.min.x),t.normal.y>0?(e+=t.normal.y*this.min.y,n+=t.normal.y*this.max.y):(e+=t.normal.y*this.max.y,n+=t.normal.y*this.min.y),t.normal.z>0?(e+=t.normal.z*this.min.z,n+=t.normal.z*this.max.z):(e+=t.normal.z*this.max.z,n+=t.normal.z*this.min.z),e<=-t.constant&&n>=-t.constant}intersectsTriangle(t){if(this.isEmpty())return!1;this.getCenter(Wr),Os.subVectors(this.max,Wr),ur.subVectors(t.a,Wr),fr.subVectors(t.b,Wr),hr.subVectors(t.c,Wr),ui.subVectors(fr,ur),fi.subVectors(hr,fr),Di.subVectors(ur,hr);let e=[0,-ui.z,ui.y,0,-fi.z,fi.y,0,-Di.z,Di.y,ui.z,0,-ui.x,fi.z,0,-fi.x,Di.z,0,-Di.x,-ui.y,ui.x,0,-fi.y,fi.x,0,-Di.y,Di.x,0];return!Mo(e,ur,fr,hr,Os)||(e=[1,0,0,0,1,0,0,0,1],!Mo(e,ur,fr,hr,Os))?!1:(Bs.crossVectors(ui,fi),e=[Bs.x,Bs.y,Bs.z],Mo(e,ur,fr,hr,Os))}clampPoint(t,e){return e.copy(t).clamp(this.min,this.max)}distanceToPoint(t){return this.clampPoint(t,mn).distanceTo(t)}getBoundingSphere(t){return this.isEmpty()?t.makeEmpty():(this.getCenter(t.center),t.radius=this.getSize(mn).length()*.5),t}intersect(t){return this.min.max(t.min),this.max.min(t.max),this.isEmpty()&&this.makeEmpty(),this}union(t){return this.min.min(t.min),this.max.max(t.max),this}applyMatrix4(t){return this.isEmpty()?this:(Hn[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(t),Hn[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(t),Hn[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(t),Hn[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(t),Hn[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(t),Hn[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(t),Hn[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(t),Hn[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(t),this.setFromPoints(Hn),this)}translate(t){return this.min.add(t),this.max.add(t),this}equals(t){return t.min.equals(this.min)&&t.max.equals(this.max)}toJSON(){return{min:this.min.toArray(),max:this.max.toArray()}}fromJSON(t){return this.min.fromArray(t.min),this.max.fromArray(t.max),this}}const Hn=[new W,new W,new W,new W,new W,new W,new W,new W],mn=new W,Fs=new Es,ur=new W,fr=new W,hr=new W,ui=new W,fi=new W,Di=new W,Wr=new W,Os=new W,Bs=new W,Li=new W;function Mo(i,t,e,n,r){for(let s=0,a=i.length-3;s<=a;s+=3){Li.fromArray(i,s);const o=r.x*Math.abs(Li.x)+r.y*Math.abs(Li.y)+r.z*Math.abs(Li.z),l=t.dot(Li),c=e.dot(Li),u=n.dot(Li);if(Math.max(-Math.max(l,c,u),Math.min(l,c,u))>o)return!1}return!0}const ge=new W,ks=new Qt;let e_=0;class Dn{constructor(t,e,n=!1){if(Array.isArray(t))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,Object.defineProperty(this,"id",{value:e_++}),this.name="",this.array=t,this.itemSize=e,this.count=t!==void 0?t.length/e:0,this.normalized=n,this.usage=pu,this.updateRanges=[],this.gpuType=wn,this.version=0}onUploadCallback(){}set needsUpdate(t){t===!0&&this.version++}setUsage(t){return this.usage=t,this}addUpdateRange(t,e){this.updateRanges.push({start:t,count:e})}clearUpdateRanges(){this.updateRanges.length=0}copy(t){return this.name=t.name,this.array=new t.array.constructor(t.array),this.itemSize=t.itemSize,this.count=t.count,this.normalized=t.normalized,this.usage=t.usage,this.gpuType=t.gpuType,this}copyAt(t,e,n){t*=this.itemSize,n*=e.itemSize;for(let r=0,s=this.itemSize;r<s;r++)this.array[t+r]=e.array[n+r];return this}copyArray(t){return this.array.set(t),this}applyMatrix3(t){if(this.itemSize===2)for(let e=0,n=this.count;e<n;e++)ks.fromBufferAttribute(this,e),ks.applyMatrix3(t),this.setXY(e,ks.x,ks.y);else if(this.itemSize===3)for(let e=0,n=this.count;e<n;e++)ge.fromBufferAttribute(this,e),ge.applyMatrix3(t),this.setXYZ(e,ge.x,ge.y,ge.z);return this}applyMatrix4(t){for(let e=0,n=this.count;e<n;e++)ge.fromBufferAttribute(this,e),ge.applyMatrix4(t),this.setXYZ(e,ge.x,ge.y,ge.z);return this}applyNormalMatrix(t){for(let e=0,n=this.count;e<n;e++)ge.fromBufferAttribute(this,e),ge.applyNormalMatrix(t),this.setXYZ(e,ge.x,ge.y,ge.z);return this}transformDirection(t){for(let e=0,n=this.count;e<n;e++)ge.fromBufferAttribute(this,e),ge.transformDirection(t),this.setXYZ(e,ge.x,ge.y,ge.z);return this}set(t,e=0){return this.array.set(t,e),this}getComponent(t,e){let n=this.array[t*this.itemSize+e];return this.normalized&&(n=Gr(n,this.array)),n}setComponent(t,e,n){return this.normalized&&(n=Be(n,this.array)),this.array[t*this.itemSize+e]=n,this}getX(t){let e=this.array[t*this.itemSize];return this.normalized&&(e=Gr(e,this.array)),e}setX(t,e){return this.normalized&&(e=Be(e,this.array)),this.array[t*this.itemSize]=e,this}getY(t){let e=this.array[t*this.itemSize+1];return this.normalized&&(e=Gr(e,this.array)),e}setY(t,e){return this.normalized&&(e=Be(e,this.array)),this.array[t*this.itemSize+1]=e,this}getZ(t){let e=this.array[t*this.itemSize+2];return this.normalized&&(e=Gr(e,this.array)),e}setZ(t,e){return this.normalized&&(e=Be(e,this.array)),this.array[t*this.itemSize+2]=e,this}getW(t){let e=this.array[t*this.itemSize+3];return this.normalized&&(e=Gr(e,this.array)),e}setW(t,e){return this.normalized&&(e=Be(e,this.array)),this.array[t*this.itemSize+3]=e,this}setXY(t,e,n){return t*=this.itemSize,this.normalized&&(e=Be(e,this.array),n=Be(n,this.array)),this.array[t+0]=e,this.array[t+1]=n,this}setXYZ(t,e,n,r){return t*=this.itemSize,this.normalized&&(e=Be(e,this.array),n=Be(n,this.array),r=Be(r,this.array)),this.array[t+0]=e,this.array[t+1]=n,this.array[t+2]=r,this}setXYZW(t,e,n,r,s){return t*=this.itemSize,this.normalized&&(e=Be(e,this.array),n=Be(n,this.array),r=Be(r,this.array),s=Be(s,this.array)),this.array[t+0]=e,this.array[t+1]=n,this.array[t+2]=r,this.array[t+3]=s,this}onUpload(t){return this.onUploadCallback=t,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const t={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(t.name=this.name),this.usage!==pu&&(t.usage=this.usage),t}}class Xh extends Dn{constructor(t,e,n){super(new Uint16Array(t),e,n)}}class qh extends Dn{constructor(t,e,n){super(new Uint32Array(t),e,n)}}class jn extends Dn{constructor(t,e,n){super(new Float32Array(t),e,n)}}const n_=new Es,Xr=new W,So=new W;class Rc{constructor(t=new W,e=-1){this.isSphere=!0,this.center=t,this.radius=e}set(t,e){return this.center.copy(t),this.radius=e,this}setFromPoints(t,e){const n=this.center;e!==void 0?n.copy(e):n_.setFromPoints(t).getCenter(n);let r=0;for(let s=0,a=t.length;s<a;s++)r=Math.max(r,n.distanceToSquared(t[s]));return this.radius=Math.sqrt(r),this}copy(t){return this.center.copy(t.center),this.radius=t.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(t){return t.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(t){return t.distanceTo(this.center)-this.radius}intersectsSphere(t){const e=this.radius+t.radius;return t.center.distanceToSquared(this.center)<=e*e}intersectsBox(t){return t.intersectsSphere(this)}intersectsPlane(t){return Math.abs(t.distanceToPoint(this.center))<=this.radius}clampPoint(t,e){const n=this.center.distanceToSquared(t);return e.copy(t),n>this.radius*this.radius&&(e.sub(this.center).normalize(),e.multiplyScalar(this.radius).add(this.center)),e}getBoundingBox(t){return this.isEmpty()?(t.makeEmpty(),t):(t.set(this.center,this.center),t.expandByScalar(this.radius),t)}applyMatrix4(t){return this.center.applyMatrix4(t),this.radius=this.radius*t.getMaxScaleOnAxis(),this}translate(t){return this.center.add(t),this}expandByPoint(t){if(this.isEmpty())return this.center.copy(t),this.radius=0,this;Xr.subVectors(t,this.center);const e=Xr.lengthSq();if(e>this.radius*this.radius){const n=Math.sqrt(e),r=(n-this.radius)*.5;this.center.addScaledVector(Xr,r/n),this.radius+=r}return this}union(t){return t.isEmpty()?this:this.isEmpty()?(this.copy(t),this):(this.center.equals(t.center)===!0?this.radius=Math.max(this.radius,t.radius):(So.subVectors(t.center,this.center).setLength(t.radius),this.expandByPoint(Xr.copy(t.center).add(So)),this.expandByPoint(Xr.copy(t.center).sub(So))),this)}equals(t){return t.center.equals(this.center)&&t.radius===this.radius}clone(){return new this.constructor().copy(this)}toJSON(){return{radius:this.radius,center:this.center.toArray()}}fromJSON(t){return this.radius=t.radius,this.center.fromArray(t.center),this}}let i_=0;const sn=new ve,yo=new tn,dr=new W,$e=new Es,qr=new Es,Te=new W;class si extends Br{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:i_++}),this.uuid=ys(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.indirectOffset=0,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(t){return Array.isArray(t)?this.index=new(Fm(t)?qh:Xh)(t,1):this.index=t,this}setIndirect(t,e=0){return this.indirect=t,this.indirectOffset=e,this}getIndirect(){return this.indirect}getAttribute(t){return this.attributes[t]}setAttribute(t,e){return this.attributes[t]=e,this}deleteAttribute(t){return delete this.attributes[t],this}hasAttribute(t){return this.attributes[t]!==void 0}addGroup(t,e,n=0){this.groups.push({start:t,count:e,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(t,e){this.drawRange.start=t,this.drawRange.count=e}applyMatrix4(t){const e=this.attributes.position;e!==void 0&&(e.applyMatrix4(t),e.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const s=new It().getNormalMatrix(t);n.applyNormalMatrix(s),n.needsUpdate=!0}const r=this.attributes.tangent;return r!==void 0&&(r.transformDirection(t),r.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(t){return sn.makeRotationFromQuaternion(t),this.applyMatrix4(sn),this}rotateX(t){return sn.makeRotationX(t),this.applyMatrix4(sn),this}rotateY(t){return sn.makeRotationY(t),this.applyMatrix4(sn),this}rotateZ(t){return sn.makeRotationZ(t),this.applyMatrix4(sn),this}translate(t,e,n){return sn.makeTranslation(t,e,n),this.applyMatrix4(sn),this}scale(t,e,n){return sn.makeScale(t,e,n),this.applyMatrix4(sn),this}lookAt(t){return yo.lookAt(t),yo.updateMatrix(),this.applyMatrix4(yo.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(dr).negate(),this.translate(dr.x,dr.y,dr.z),this}setFromPoints(t){const e=this.getAttribute("position");if(e===void 0){const n=[];for(let r=0,s=t.length;r<s;r++){const a=t[r];n.push(a.x,a.y,a.z||0)}this.setAttribute("position",new jn(n,3))}else{const n=Math.min(t.length,e.count);for(let r=0;r<n;r++){const s=t[r];e.setXYZ(r,s.x,s.y,s.z||0)}t.length>e.count&&Pt("BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),e.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new Es);const t=this.attributes.position,e=this.morphAttributes.position;if(t&&t.isGLBufferAttribute){Xt("BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new W(-1/0,-1/0,-1/0),new W(1/0,1/0,1/0));return}if(t!==void 0){if(this.boundingBox.setFromBufferAttribute(t),e)for(let n=0,r=e.length;n<r;n++){const s=e[n];$e.setFromBufferAttribute(s),this.morphTargetsRelative?(Te.addVectors(this.boundingBox.min,$e.min),this.boundingBox.expandByPoint(Te),Te.addVectors(this.boundingBox.max,$e.max),this.boundingBox.expandByPoint(Te)):(this.boundingBox.expandByPoint($e.min),this.boundingBox.expandByPoint($e.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&Xt('BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Rc);const t=this.attributes.position,e=this.morphAttributes.position;if(t&&t.isGLBufferAttribute){Xt("BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new W,1/0);return}if(t){const n=this.boundingSphere.center;if($e.setFromBufferAttribute(t),e)for(let s=0,a=e.length;s<a;s++){const o=e[s];qr.setFromBufferAttribute(o),this.morphTargetsRelative?(Te.addVectors($e.min,qr.min),$e.expandByPoint(Te),Te.addVectors($e.max,qr.max),$e.expandByPoint(Te)):($e.expandByPoint(qr.min),$e.expandByPoint(qr.max))}$e.getCenter(n);let r=0;for(let s=0,a=t.count;s<a;s++)Te.fromBufferAttribute(t,s),r=Math.max(r,n.distanceToSquared(Te));if(e)for(let s=0,a=e.length;s<a;s++){const o=e[s],l=this.morphTargetsRelative;for(let c=0,u=o.count;c<u;c++)Te.fromBufferAttribute(o,c),l&&(dr.fromBufferAttribute(t,c),Te.add(dr)),r=Math.max(r,n.distanceToSquared(Te))}this.boundingSphere.radius=Math.sqrt(r),isNaN(this.boundingSphere.radius)&&Xt('BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const t=this.index,e=this.attributes;if(t===null||e.position===void 0||e.normal===void 0||e.uv===void 0){Xt("BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=e.position,r=e.normal,s=e.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new Dn(new Float32Array(4*n.count),4));const a=this.getAttribute("tangent"),o=[],l=[];for(let x=0;x<n.count;x++)o[x]=new W,l[x]=new W;const c=new W,u=new W,h=new W,f=new Qt,d=new Qt,_=new Qt,g=new W,p=new W;function m(x,y,G){c.fromBufferAttribute(n,x),u.fromBufferAttribute(n,y),h.fromBufferAttribute(n,G),f.fromBufferAttribute(s,x),d.fromBufferAttribute(s,y),_.fromBufferAttribute(s,G),u.sub(c),h.sub(c),d.sub(f),_.sub(f);const D=1/(d.x*_.y-_.x*d.y);isFinite(D)&&(g.copy(u).multiplyScalar(_.y).addScaledVector(h,-d.y).multiplyScalar(D),p.copy(h).multiplyScalar(d.x).addScaledVector(u,-_.x).multiplyScalar(D),o[x].add(g),o[y].add(g),o[G].add(g),l[x].add(p),l[y].add(p),l[G].add(p))}let M=this.groups;M.length===0&&(M=[{start:0,count:t.count}]);for(let x=0,y=M.length;x<y;++x){const G=M[x],D=G.start,B=G.count;for(let k=D,X=D+B;k<X;k+=3)m(t.getX(k+0),t.getX(k+1),t.getX(k+2))}const T=new W,S=new W,b=new W,A=new W;function R(x){b.fromBufferAttribute(r,x),A.copy(b);const y=o[x];T.copy(y),T.sub(b.multiplyScalar(b.dot(y))).normalize(),S.crossVectors(A,y);const D=S.dot(l[x])<0?-1:1;a.setXYZW(x,T.x,T.y,T.z,D)}for(let x=0,y=M.length;x<y;++x){const G=M[x],D=G.start,B=G.count;for(let k=D,X=D+B;k<X;k+=3)R(t.getX(k+0)),R(t.getX(k+1)),R(t.getX(k+2))}}computeVertexNormals(){const t=this.index,e=this.getAttribute("position");if(e!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new Dn(new Float32Array(e.count*3),3),this.setAttribute("normal",n);else for(let f=0,d=n.count;f<d;f++)n.setXYZ(f,0,0,0);const r=new W,s=new W,a=new W,o=new W,l=new W,c=new W,u=new W,h=new W;if(t)for(let f=0,d=t.count;f<d;f+=3){const _=t.getX(f+0),g=t.getX(f+1),p=t.getX(f+2);r.fromBufferAttribute(e,_),s.fromBufferAttribute(e,g),a.fromBufferAttribute(e,p),u.subVectors(a,s),h.subVectors(r,s),u.cross(h),o.fromBufferAttribute(n,_),l.fromBufferAttribute(n,g),c.fromBufferAttribute(n,p),o.add(u),l.add(u),c.add(u),n.setXYZ(_,o.x,o.y,o.z),n.setXYZ(g,l.x,l.y,l.z),n.setXYZ(p,c.x,c.y,c.z)}else for(let f=0,d=e.count;f<d;f+=3)r.fromBufferAttribute(e,f+0),s.fromBufferAttribute(e,f+1),a.fromBufferAttribute(e,f+2),u.subVectors(a,s),h.subVectors(r,s),u.cross(h),n.setXYZ(f+0,u.x,u.y,u.z),n.setXYZ(f+1,u.x,u.y,u.z),n.setXYZ(f+2,u.x,u.y,u.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const t=this.attributes.normal;for(let e=0,n=t.count;e<n;e++)Te.fromBufferAttribute(t,e),Te.normalize(),t.setXYZ(e,Te.x,Te.y,Te.z)}toNonIndexed(){function t(o,l){const c=o.array,u=o.itemSize,h=o.normalized,f=new c.constructor(l.length*u);let d=0,_=0;for(let g=0,p=l.length;g<p;g++){o.isInterleavedBufferAttribute?d=l[g]*o.data.stride+o.offset:d=l[g]*u;for(let m=0;m<u;m++)f[_++]=c[d++]}return new Dn(f,u,h)}if(this.index===null)return Pt("BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const e=new si,n=this.index.array,r=this.attributes;for(const o in r){const l=r[o],c=t(l,n);e.setAttribute(o,c)}const s=this.morphAttributes;for(const o in s){const l=[],c=s[o];for(let u=0,h=c.length;u<h;u++){const f=c[u],d=t(f,n);l.push(d)}e.morphAttributes[o]=l}e.morphTargetsRelative=this.morphTargetsRelative;const a=this.groups;for(let o=0,l=a.length;o<l;o++){const c=a[o];e.addGroup(c.start,c.count,c.materialIndex)}return e}toJSON(){const t={metadata:{version:4.7,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(t.uuid=this.uuid,t.type=this.type,this.name!==""&&(t.name=this.name),Object.keys(this.userData).length>0&&(t.userData=this.userData),this.parameters!==void 0){const l=this.parameters;for(const c in l)l[c]!==void 0&&(t[c]=l[c]);return t}t.data={attributes:{}};const e=this.index;e!==null&&(t.data.index={type:e.array.constructor.name,array:Array.prototype.slice.call(e.array)});const n=this.attributes;for(const l in n){const c=n[l];t.data.attributes[l]=c.toJSON(t.data)}const r={};let s=!1;for(const l in this.morphAttributes){const c=this.morphAttributes[l],u=[];for(let h=0,f=c.length;h<f;h++){const d=c[h];u.push(d.toJSON(t.data))}u.length>0&&(r[l]=u,s=!0)}s&&(t.data.morphAttributes=r,t.data.morphTargetsRelative=this.morphTargetsRelative);const a=this.groups;a.length>0&&(t.data.groups=JSON.parse(JSON.stringify(a)));const o=this.boundingSphere;return o!==null&&(t.data.boundingSphere=o.toJSON()),t}clone(){return new this.constructor().copy(this)}copy(t){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const e={};this.name=t.name;const n=t.index;n!==null&&this.setIndex(n.clone());const r=t.attributes;for(const c in r){const u=r[c];this.setAttribute(c,u.clone(e))}const s=t.morphAttributes;for(const c in s){const u=[],h=s[c];for(let f=0,d=h.length;f<d;f++)u.push(h[f].clone(e));this.morphAttributes[c]=u}this.morphTargetsRelative=t.morphTargetsRelative;const a=t.groups;for(let c=0,u=a.length;c<u;c++){const h=a[c];this.addGroup(h.start,h.count,h.materialIndex)}const o=t.boundingBox;o!==null&&(this.boundingBox=o.clone());const l=t.boundingSphere;return l!==null&&(this.boundingSphere=l.clone()),this.drawRange.start=t.drawRange.start,this.drawRange.count=t.drawRange.count,this.userData=t.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}let r_=0;class Ba extends Br{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:r_++}),this.uuid=ys(),this.name="",this.type="Material",this.blending=yr,this.side=bi,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=jo,this.blendDst=Qo,this.blendEquation=zi,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new Zt(0,0,0),this.blendAlpha=0,this.depthFunc=Dr,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=du,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=ir,this.stencilZFail=ir,this.stencilZPass=ir,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.allowOverride=!0,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(t){this._alphaTest>0!=t>0&&this.version++,this._alphaTest=t}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(t){if(t!==void 0)for(const e in t){const n=t[e];if(n===void 0){Pt(`Material: parameter '${e}' has value of undefined.`);continue}const r=this[e];if(r===void 0){Pt(`Material: '${e}' is not a property of THREE.${this.type}.`);continue}r&&r.isColor?r.set(n):r&&r.isVector3&&n&&n.isVector3?r.copy(n):this[e]=n}}toJSON(t){const e=t===void 0||typeof t=="string";e&&(t={textures:{},images:{}});const n={metadata:{version:4.7,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(t).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(t).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(t).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.sheenColorMap&&this.sheenColorMap.isTexture&&(n.sheenColorMap=this.sheenColorMap.toJSON(t).uuid),this.sheenRoughnessMap&&this.sheenRoughnessMap.isTexture&&(n.sheenRoughnessMap=this.sheenRoughnessMap.toJSON(t).uuid),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(t).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(t).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(t).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(t).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(t).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(t).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(t).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(t).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(t).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(t).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(t).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(t).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(t).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(t).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(t).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(t).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(t).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(t).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(t).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(t).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(t).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==yr&&(n.blending=this.blending),this.side!==bi&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==jo&&(n.blendSrc=this.blendSrc),this.blendDst!==Qo&&(n.blendDst=this.blendDst),this.blendEquation!==zi&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==Dr&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==du&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==ir&&(n.stencilFail=this.stencilFail),this.stencilZFail!==ir&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==ir&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.allowOverride===!1&&(n.allowOverride=!1),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function r(s){const a=[];for(const o in s){const l=s[o];delete l.metadata,a.push(l)}return a}if(e){const s=r(t.textures),a=r(t.images);s.length>0&&(n.textures=s),a.length>0&&(n.images=a)}return n}clone(){return new this.constructor().copy(this)}copy(t){this.name=t.name,this.blending=t.blending,this.side=t.side,this.vertexColors=t.vertexColors,this.opacity=t.opacity,this.transparent=t.transparent,this.blendSrc=t.blendSrc,this.blendDst=t.blendDst,this.blendEquation=t.blendEquation,this.blendSrcAlpha=t.blendSrcAlpha,this.blendDstAlpha=t.blendDstAlpha,this.blendEquationAlpha=t.blendEquationAlpha,this.blendColor.copy(t.blendColor),this.blendAlpha=t.blendAlpha,this.depthFunc=t.depthFunc,this.depthTest=t.depthTest,this.depthWrite=t.depthWrite,this.stencilWriteMask=t.stencilWriteMask,this.stencilFunc=t.stencilFunc,this.stencilRef=t.stencilRef,this.stencilFuncMask=t.stencilFuncMask,this.stencilFail=t.stencilFail,this.stencilZFail=t.stencilZFail,this.stencilZPass=t.stencilZPass,this.stencilWrite=t.stencilWrite;const e=t.clippingPlanes;let n=null;if(e!==null){const r=e.length;n=new Array(r);for(let s=0;s!==r;++s)n[s]=e[s].clone()}return this.clippingPlanes=n,this.clipIntersection=t.clipIntersection,this.clipShadows=t.clipShadows,this.shadowSide=t.shadowSide,this.colorWrite=t.colorWrite,this.precision=t.precision,this.polygonOffset=t.polygonOffset,this.polygonOffsetFactor=t.polygonOffsetFactor,this.polygonOffsetUnits=t.polygonOffsetUnits,this.dithering=t.dithering,this.alphaTest=t.alphaTest,this.alphaHash=t.alphaHash,this.alphaToCoverage=t.alphaToCoverage,this.premultipliedAlpha=t.premultipliedAlpha,this.forceSinglePass=t.forceSinglePass,this.allowOverride=t.allowOverride,this.visible=t.visible,this.toneMapped=t.toneMapped,this.userData=JSON.parse(JSON.stringify(t.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(t){t===!0&&this.version++}}const Wn=new W,Eo=new W,zs=new W,hi=new W,To=new W,Vs=new W,bo=new W;class s_{constructor(t=new W,e=new W(0,0,-1)){this.origin=t,this.direction=e}set(t,e){return this.origin.copy(t),this.direction.copy(e),this}copy(t){return this.origin.copy(t.origin),this.direction.copy(t.direction),this}at(t,e){return e.copy(this.origin).addScaledVector(this.direction,t)}lookAt(t){return this.direction.copy(t).sub(this.origin).normalize(),this}recast(t){return this.origin.copy(this.at(t,Wn)),this}closestPointToPoint(t,e){e.subVectors(t,this.origin);const n=e.dot(this.direction);return n<0?e.copy(this.origin):e.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(t){return Math.sqrt(this.distanceSqToPoint(t))}distanceSqToPoint(t){const e=Wn.subVectors(t,this.origin).dot(this.direction);return e<0?this.origin.distanceToSquared(t):(Wn.copy(this.origin).addScaledVector(this.direction,e),Wn.distanceToSquared(t))}distanceSqToSegment(t,e,n,r){Eo.copy(t).add(e).multiplyScalar(.5),zs.copy(e).sub(t).normalize(),hi.copy(this.origin).sub(Eo);const s=t.distanceTo(e)*.5,a=-this.direction.dot(zs),o=hi.dot(this.direction),l=-hi.dot(zs),c=hi.lengthSq(),u=Math.abs(1-a*a);let h,f,d,_;if(u>0)if(h=a*l-o,f=a*o-l,_=s*u,h>=0)if(f>=-_)if(f<=_){const g=1/u;h*=g,f*=g,d=h*(h+a*f+2*o)+f*(a*h+f+2*l)+c}else f=s,h=Math.max(0,-(a*f+o)),d=-h*h+f*(f+2*l)+c;else f=-s,h=Math.max(0,-(a*f+o)),d=-h*h+f*(f+2*l)+c;else f<=-_?(h=Math.max(0,-(-a*s+o)),f=h>0?-s:Math.min(Math.max(-s,-l),s),d=-h*h+f*(f+2*l)+c):f<=_?(h=0,f=Math.min(Math.max(-s,-l),s),d=f*(f+2*l)+c):(h=Math.max(0,-(a*s+o)),f=h>0?s:Math.min(Math.max(-s,-l),s),d=-h*h+f*(f+2*l)+c);else f=a>0?-s:s,h=Math.max(0,-(a*f+o)),d=-h*h+f*(f+2*l)+c;return n&&n.copy(this.origin).addScaledVector(this.direction,h),r&&r.copy(Eo).addScaledVector(zs,f),d}intersectSphere(t,e){Wn.subVectors(t.center,this.origin);const n=Wn.dot(this.direction),r=Wn.dot(Wn)-n*n,s=t.radius*t.radius;if(r>s)return null;const a=Math.sqrt(s-r),o=n-a,l=n+a;return l<0?null:o<0?this.at(l,e):this.at(o,e)}intersectsSphere(t){return t.radius<0?!1:this.distanceSqToPoint(t.center)<=t.radius*t.radius}distanceToPlane(t){const e=t.normal.dot(this.direction);if(e===0)return t.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(t.normal)+t.constant)/e;return n>=0?n:null}intersectPlane(t,e){const n=this.distanceToPlane(t);return n===null?null:this.at(n,e)}intersectsPlane(t){const e=t.distanceToPoint(this.origin);return e===0||t.normal.dot(this.direction)*e<0}intersectBox(t,e){let n,r,s,a,o,l;const c=1/this.direction.x,u=1/this.direction.y,h=1/this.direction.z,f=this.origin;return c>=0?(n=(t.min.x-f.x)*c,r=(t.max.x-f.x)*c):(n=(t.max.x-f.x)*c,r=(t.min.x-f.x)*c),u>=0?(s=(t.min.y-f.y)*u,a=(t.max.y-f.y)*u):(s=(t.max.y-f.y)*u,a=(t.min.y-f.y)*u),n>a||s>r||((s>n||isNaN(n))&&(n=s),(a<r||isNaN(r))&&(r=a),h>=0?(o=(t.min.z-f.z)*h,l=(t.max.z-f.z)*h):(o=(t.max.z-f.z)*h,l=(t.min.z-f.z)*h),n>l||o>r)||((o>n||n!==n)&&(n=o),(l<r||r!==r)&&(r=l),r<0)?null:this.at(n>=0?n:r,e)}intersectsBox(t){return this.intersectBox(t,Wn)!==null}intersectTriangle(t,e,n,r,s){To.subVectors(e,t),Vs.subVectors(n,t),bo.crossVectors(To,Vs);let a=this.direction.dot(bo),o;if(a>0){if(r)return null;o=1}else if(a<0)o=-1,a=-a;else return null;hi.subVectors(this.origin,t);const l=o*this.direction.dot(Vs.crossVectors(hi,Vs));if(l<0)return null;const c=o*this.direction.dot(To.cross(hi));if(c<0||l+c>a)return null;const u=-o*hi.dot(bo);return u<0?null:this.at(u/a,s)}applyMatrix4(t){return this.origin.applyMatrix4(t),this.direction.transformDirection(t),this}equals(t){return t.origin.equals(this.origin)&&t.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class Cc extends Ba{constructor(t){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new Zt(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new ii,this.combine=bh,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(t)}copy(t){return super.copy(t),this.color.copy(t.color),this.map=t.map,this.lightMap=t.lightMap,this.lightMapIntensity=t.lightMapIntensity,this.aoMap=t.aoMap,this.aoMapIntensity=t.aoMapIntensity,this.specularMap=t.specularMap,this.alphaMap=t.alphaMap,this.envMap=t.envMap,this.envMapRotation.copy(t.envMapRotation),this.combine=t.combine,this.reflectivity=t.reflectivity,this.refractionRatio=t.refractionRatio,this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this.wireframeLinecap=t.wireframeLinecap,this.wireframeLinejoin=t.wireframeLinejoin,this.fog=t.fog,this}}const Cu=new ve,Ii=new s_,Gs=new Rc,Pu=new W,Hs=new W,Ws=new W,Xs=new W,Ao=new W,qs=new W,Du=new W,Ys=new W;class Nn extends tn{constructor(t=new si,e=new Cc){super(),this.isMesh=!0,this.type="Mesh",this.geometry=t,this.material=e,this.morphTargetDictionary=void 0,this.morphTargetInfluences=void 0,this.count=1,this.updateMorphTargets()}copy(t,e){return super.copy(t,e),t.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=t.morphTargetInfluences.slice()),t.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},t.morphTargetDictionary)),this.material=Array.isArray(t.material)?t.material.slice():t.material,this.geometry=t.geometry,this}updateMorphTargets(){const e=this.geometry.morphAttributes,n=Object.keys(e);if(n.length>0){const r=e[n[0]];if(r!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=r.length;s<a;s++){const o=r[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[o]=s}}}}getVertexPosition(t,e){const n=this.geometry,r=n.attributes.position,s=n.morphAttributes.position,a=n.morphTargetsRelative;e.fromBufferAttribute(r,t);const o=this.morphTargetInfluences;if(s&&o){qs.set(0,0,0);for(let l=0,c=s.length;l<c;l++){const u=o[l],h=s[l];u!==0&&(Ao.fromBufferAttribute(h,t),a?qs.addScaledVector(Ao,u):qs.addScaledVector(Ao.sub(e),u))}e.add(qs)}return e}raycast(t,e){const n=this.geometry,r=this.material,s=this.matrixWorld;r!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),Gs.copy(n.boundingSphere),Gs.applyMatrix4(s),Ii.copy(t.ray).recast(t.near),!(Gs.containsPoint(Ii.origin)===!1&&(Ii.intersectSphere(Gs,Pu)===null||Ii.origin.distanceToSquared(Pu)>(t.far-t.near)**2))&&(Cu.copy(s).invert(),Ii.copy(t.ray).applyMatrix4(Cu),!(n.boundingBox!==null&&Ii.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(t,e,Ii)))}_computeIntersections(t,e,n){let r;const s=this.geometry,a=this.material,o=s.index,l=s.attributes.position,c=s.attributes.uv,u=s.attributes.uv1,h=s.attributes.normal,f=s.groups,d=s.drawRange;if(o!==null)if(Array.isArray(a))for(let _=0,g=f.length;_<g;_++){const p=f[_],m=a[p.materialIndex],M=Math.max(p.start,d.start),T=Math.min(o.count,Math.min(p.start+p.count,d.start+d.count));for(let S=M,b=T;S<b;S+=3){const A=o.getX(S),R=o.getX(S+1),x=o.getX(S+2);r=$s(this,m,t,n,c,u,h,A,R,x),r&&(r.faceIndex=Math.floor(S/3),r.face.materialIndex=p.materialIndex,e.push(r))}}else{const _=Math.max(0,d.start),g=Math.min(o.count,d.start+d.count);for(let p=_,m=g;p<m;p+=3){const M=o.getX(p),T=o.getX(p+1),S=o.getX(p+2);r=$s(this,a,t,n,c,u,h,M,T,S),r&&(r.faceIndex=Math.floor(p/3),e.push(r))}}else if(l!==void 0)if(Array.isArray(a))for(let _=0,g=f.length;_<g;_++){const p=f[_],m=a[p.materialIndex],M=Math.max(p.start,d.start),T=Math.min(l.count,Math.min(p.start+p.count,d.start+d.count));for(let S=M,b=T;S<b;S+=3){const A=S,R=S+1,x=S+2;r=$s(this,m,t,n,c,u,h,A,R,x),r&&(r.faceIndex=Math.floor(S/3),r.face.materialIndex=p.materialIndex,e.push(r))}}else{const _=Math.max(0,d.start),g=Math.min(l.count,d.start+d.count);for(let p=_,m=g;p<m;p+=3){const M=p,T=p+1,S=p+2;r=$s(this,a,t,n,c,u,h,M,T,S),r&&(r.faceIndex=Math.floor(p/3),e.push(r))}}}}function a_(i,t,e,n,r,s,a,o){let l;if(t.side===We?l=n.intersectTriangle(a,s,r,!0,o):l=n.intersectTriangle(r,s,a,t.side===bi,o),l===null)return null;Ys.copy(o),Ys.applyMatrix4(i.matrixWorld);const c=e.ray.origin.distanceTo(Ys);return c<e.near||c>e.far?null:{distance:c,point:Ys.clone(),object:i}}function $s(i,t,e,n,r,s,a,o,l,c){i.getVertexPosition(o,Hs),i.getVertexPosition(l,Ws),i.getVertexPosition(c,Xs);const u=a_(i,t,e,n,Hs,Ws,Xs,Du);if(u){const h=new W;_n.getBarycoord(Du,Hs,Ws,Xs,h),r&&(u.uv=_n.getInterpolatedAttribute(r,o,l,c,h,new Qt)),s&&(u.uv1=_n.getInterpolatedAttribute(s,o,l,c,h,new Qt)),a&&(u.normal=_n.getInterpolatedAttribute(a,o,l,c,h,new W),u.normal.dot(n.direction)>0&&u.normal.multiplyScalar(-1));const f={a:o,b:l,c,normal:new W,materialIndex:0};_n.getNormal(Hs,Ws,Xs,f.normal),u.face=f,u.barycoord=h}return u}class o_ extends Oe{constructor(t=null,e=1,n=1,r,s,a,o,l,c=we,u=we,h,f){super(null,a,o,l,c,u,r,s,h,f),this.isDataTexture=!0,this.image={data:t,width:e,height:n},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const wo=new W,l_=new W,c_=new It;class Bi{constructor(t=new W(1,0,0),e=0){this.isPlane=!0,this.normal=t,this.constant=e}set(t,e){return this.normal.copy(t),this.constant=e,this}setComponents(t,e,n,r){return this.normal.set(t,e,n),this.constant=r,this}setFromNormalAndCoplanarPoint(t,e){return this.normal.copy(t),this.constant=-e.dot(this.normal),this}setFromCoplanarPoints(t,e,n){const r=wo.subVectors(n,e).cross(l_.subVectors(t,e)).normalize();return this.setFromNormalAndCoplanarPoint(r,t),this}copy(t){return this.normal.copy(t.normal),this.constant=t.constant,this}normalize(){const t=1/this.normal.length();return this.normal.multiplyScalar(t),this.constant*=t,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(t){return this.normal.dot(t)+this.constant}distanceToSphere(t){return this.distanceToPoint(t.center)-t.radius}projectPoint(t,e){return e.copy(t).addScaledVector(this.normal,-this.distanceToPoint(t))}intersectLine(t,e){const n=t.delta(wo),r=this.normal.dot(n);if(r===0)return this.distanceToPoint(t.start)===0?e.copy(t.start):null;const s=-(t.start.dot(this.normal)+this.constant)/r;return s<0||s>1?null:e.copy(t.start).addScaledVector(n,s)}intersectsLine(t){const e=this.distanceToPoint(t.start),n=this.distanceToPoint(t.end);return e<0&&n>0||n<0&&e>0}intersectsBox(t){return t.intersectsPlane(this)}intersectsSphere(t){return t.intersectsPlane(this)}coplanarPoint(t){return t.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(t,e){const n=e||c_.getNormalMatrix(t),r=this.coplanarPoint(wo).applyMatrix4(t),s=this.normal.applyMatrix3(n).normalize();return this.constant=-r.dot(s),this}translate(t){return this.constant-=t.dot(this.normal),this}equals(t){return t.normal.equals(this.normal)&&t.constant===this.constant}clone(){return new this.constructor().copy(this)}}const Ui=new Rc,u_=new Qt(.5,.5),Ks=new W;class Yh{constructor(t=new Bi,e=new Bi,n=new Bi,r=new Bi,s=new Bi,a=new Bi){this.planes=[t,e,n,r,s,a]}set(t,e,n,r,s,a){const o=this.planes;return o[0].copy(t),o[1].copy(e),o[2].copy(n),o[3].copy(r),o[4].copy(s),o[5].copy(a),this}copy(t){const e=this.planes;for(let n=0;n<6;n++)e[n].copy(t.planes[n]);return this}setFromProjectionMatrix(t,e=Rn,n=!1){const r=this.planes,s=t.elements,a=s[0],o=s[1],l=s[2],c=s[3],u=s[4],h=s[5],f=s[6],d=s[7],_=s[8],g=s[9],p=s[10],m=s[11],M=s[12],T=s[13],S=s[14],b=s[15];if(r[0].setComponents(c-a,d-u,m-_,b-M).normalize(),r[1].setComponents(c+a,d+u,m+_,b+M).normalize(),r[2].setComponents(c+o,d+h,m+g,b+T).normalize(),r[3].setComponents(c-o,d-h,m-g,b-T).normalize(),n)r[4].setComponents(l,f,p,S).normalize(),r[5].setComponents(c-l,d-f,m-p,b-S).normalize();else if(r[4].setComponents(c-l,d-f,m-p,b-S).normalize(),e===Rn)r[5].setComponents(c+l,d+f,m+p,b+S).normalize();else if(e===Ta)r[5].setComponents(l,f,p,S).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+e);return this}intersectsObject(t){if(t.boundingSphere!==void 0)t.boundingSphere===null&&t.computeBoundingSphere(),Ui.copy(t.boundingSphere).applyMatrix4(t.matrixWorld);else{const e=t.geometry;e.boundingSphere===null&&e.computeBoundingSphere(),Ui.copy(e.boundingSphere).applyMatrix4(t.matrixWorld)}return this.intersectsSphere(Ui)}intersectsSprite(t){Ui.center.set(0,0,0);const e=u_.distanceTo(t.center);return Ui.radius=.7071067811865476+e,Ui.applyMatrix4(t.matrixWorld),this.intersectsSphere(Ui)}intersectsSphere(t){const e=this.planes,n=t.center,r=-t.radius;for(let s=0;s<6;s++)if(e[s].distanceToPoint(n)<r)return!1;return!0}intersectsBox(t){const e=this.planes;for(let n=0;n<6;n++){const r=e[n];if(Ks.x=r.normal.x>0?t.max.x:t.min.x,Ks.y=r.normal.y>0?t.max.y:t.min.y,Ks.z=r.normal.z>0?t.max.z:t.min.z,r.distanceToPoint(Ks)<0)return!1}return!0}containsPoint(t){const e=this.planes;for(let n=0;n<6;n++)if(e[n].distanceToPoint(t)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}class $h extends Oe{constructor(t=[],e=Ji,n,r,s,a,o,l,c,u){super(t,e,n,r,s,a,o,l,c,u),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(t){this.image=t}}class _s extends Oe{constructor(t,e,n=Un,r,s,a,o=we,l=we,c,u=ni,h=1){if(u!==ni&&u!==Wi)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");const f={width:t,height:e,depth:h};super(f,r,s,a,o,l,u,n,c),this.isDepthTexture=!0,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(t){return super.copy(t),this.source=new wc(Object.assign({},t.image)),this.compareFunction=t.compareFunction,this}toJSON(t){const e=super.toJSON(t);return this.compareFunction!==null&&(e.compareFunction=this.compareFunction),e}}class f_ extends _s{constructor(t,e=Un,n=Ji,r,s,a=we,o=we,l,c=ni){const u={width:t,height:t,depth:1},h=[u,u,u,u,u,u];super(t,t,e,n,r,s,a,o,l,c),this.image=h,this.isCubeDepthTexture=!0,this.isCubeTexture=!0}get images(){return this.image}set images(t){this.image=t}}class Kh extends Oe{constructor(t=null){super(),this.sourceTexture=t,this.isExternalTexture=!0}copy(t){return super.copy(t),this.sourceTexture=t.sourceTexture,this}}class Ts extends si{constructor(t=1,e=1,n=1,r=1,s=1,a=1){super(),this.type="BoxGeometry",this.parameters={width:t,height:e,depth:n,widthSegments:r,heightSegments:s,depthSegments:a};const o=this;r=Math.floor(r),s=Math.floor(s),a=Math.floor(a);const l=[],c=[],u=[],h=[];let f=0,d=0;_("z","y","x",-1,-1,n,e,t,a,s,0),_("z","y","x",1,-1,n,e,-t,a,s,1),_("x","z","y",1,1,t,n,e,r,a,2),_("x","z","y",1,-1,t,n,-e,r,a,3),_("x","y","z",1,-1,t,e,n,r,s,4),_("x","y","z",-1,-1,t,e,-n,r,s,5),this.setIndex(l),this.setAttribute("position",new jn(c,3)),this.setAttribute("normal",new jn(u,3)),this.setAttribute("uv",new jn(h,2));function _(g,p,m,M,T,S,b,A,R,x,y){const G=S/R,D=b/x,B=S/2,k=b/2,X=A/2,C=R+1,L=x+1;let P=0,z=0;const O=new W;for(let J=0;J<L;J++){const Q=J*D-k;for(let st=0;st<C;st++){const bt=st*G-B;O[g]=bt*M,O[p]=Q*T,O[m]=X,c.push(O.x,O.y,O.z),O[g]=0,O[p]=0,O[m]=A>0?1:-1,u.push(O.x,O.y,O.z),h.push(st/R),h.push(1-J/x),P+=1}}for(let J=0;J<x;J++)for(let Q=0;Q<R;Q++){const st=f+Q+C*J,bt=f+Q+C*(J+1),Ut=f+(Q+1)+C*(J+1),Ft=f+(Q+1)+C*J;l.push(st,bt,Ft),l.push(bt,Ut,Ft),z+=6}o.addGroup(d,z,y),d+=z,f+=P}}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new Ts(t.width,t.height,t.depth,t.widthSegments,t.heightSegments,t.depthSegments)}}class bs extends si{constructor(t=1,e=1,n=1,r=1){super(),this.type="PlaneGeometry",this.parameters={width:t,height:e,widthSegments:n,heightSegments:r};const s=t/2,a=e/2,o=Math.floor(n),l=Math.floor(r),c=o+1,u=l+1,h=t/o,f=e/l,d=[],_=[],g=[],p=[];for(let m=0;m<u;m++){const M=m*f-a;for(let T=0;T<c;T++){const S=T*h-s;_.push(S,-M,0),g.push(0,0,1),p.push(T/o),p.push(1-m/l)}}for(let m=0;m<l;m++)for(let M=0;M<o;M++){const T=M+c*m,S=M+c*(m+1),b=M+1+c*(m+1),A=M+1+c*m;d.push(T,S,A),d.push(S,b,A)}this.setIndex(d),this.setAttribute("position",new jn(_,3)),this.setAttribute("normal",new jn(g,3)),this.setAttribute("uv",new jn(p,2))}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new bs(t.width,t.height,t.widthSegments,t.heightSegments)}}function Nr(i){const t={};for(const e in i){t[e]={};for(const n in i[e]){const r=i[e][n];r&&(r.isColor||r.isMatrix3||r.isMatrix4||r.isVector2||r.isVector3||r.isVector4||r.isTexture||r.isQuaternion)?r.isRenderTargetTexture?(Pt("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),t[e][n]=null):t[e][n]=r.clone():Array.isArray(r)?t[e][n]=r.slice():t[e][n]=r}}return t}function Ne(i){const t={};for(let e=0;e<i.length;e++){const n=Nr(i[e]);for(const r in n)t[r]=n[r]}return t}function h_(i){const t=[];for(let e=0;e<i.length;e++)t.push(i[e].clone());return t}function Zh(i){const t=i.getRenderTarget();return t===null?i.outputColorSpace:t.isXRRenderTarget===!0?t.texture.colorSpace:Ht.workingColorSpace}const d_={clone:Nr,merge:Ne};var p_=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,m_=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class Fn extends Ba{constructor(t){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=p_,this.fragmentShader=m_,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,t!==void 0&&this.setValues(t)}copy(t){return super.copy(t),this.fragmentShader=t.fragmentShader,this.vertexShader=t.vertexShader,this.uniforms=Nr(t.uniforms),this.uniformsGroups=h_(t.uniformsGroups),this.defines=Object.assign({},t.defines),this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this.fog=t.fog,this.lights=t.lights,this.clipping=t.clipping,this.extensions=Object.assign({},t.extensions),this.glslVersion=t.glslVersion,this.defaultAttributeValues=Object.assign({},t.defaultAttributeValues),this.index0AttributeName=t.index0AttributeName,this.uniformsNeedUpdate=t.uniformsNeedUpdate,this}toJSON(t){const e=super.toJSON(t);e.glslVersion=this.glslVersion,e.uniforms={};for(const r in this.uniforms){const a=this.uniforms[r].value;a&&a.isTexture?e.uniforms[r]={type:"t",value:a.toJSON(t).uuid}:a&&a.isColor?e.uniforms[r]={type:"c",value:a.getHex()}:a&&a.isVector2?e.uniforms[r]={type:"v2",value:a.toArray()}:a&&a.isVector3?e.uniforms[r]={type:"v3",value:a.toArray()}:a&&a.isVector4?e.uniforms[r]={type:"v4",value:a.toArray()}:a&&a.isMatrix3?e.uniforms[r]={type:"m3",value:a.toArray()}:a&&a.isMatrix4?e.uniforms[r]={type:"m4",value:a.toArray()}:e.uniforms[r]={value:a}}Object.keys(this.defines).length>0&&(e.defines=this.defines),e.vertexShader=this.vertexShader,e.fragmentShader=this.fragmentShader,e.lights=this.lights,e.clipping=this.clipping;const n={};for(const r in this.extensions)this.extensions[r]===!0&&(n[r]=!0);return Object.keys(n).length>0&&(e.extensions=n),e}}class __ extends Fn{constructor(t){super(t),this.isRawShaderMaterial=!0,this.type="RawShaderMaterial"}}class g_ extends Ba{constructor(t){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=wm,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(t)}copy(t){return super.copy(t),this.depthPacking=t.depthPacking,this.map=t.map,this.alphaMap=t.alphaMap,this.displacementMap=t.displacementMap,this.displacementScale=t.displacementScale,this.displacementBias=t.displacementBias,this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this}}class x_ extends Ba{constructor(t){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(t)}copy(t){return super.copy(t),this.map=t.map,this.alphaMap=t.alphaMap,this.displacementMap=t.displacementMap,this.displacementScale=t.displacementScale,this.displacementBias=t.displacementBias,this}}const Zs=new W,Js=new kr,Sn=new W;class Jh extends tn{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new ve,this.projectionMatrix=new ve,this.projectionMatrixInverse=new ve,this.coordinateSystem=Rn,this._reversedDepth=!1}get reversedDepth(){return this._reversedDepth}copy(t,e){return super.copy(t,e),this.matrixWorldInverse.copy(t.matrixWorldInverse),this.projectionMatrix.copy(t.projectionMatrix),this.projectionMatrixInverse.copy(t.projectionMatrixInverse),this.coordinateSystem=t.coordinateSystem,this}getWorldDirection(t){return super.getWorldDirection(t).negate()}updateMatrixWorld(t){super.updateMatrixWorld(t),this.matrixWorld.decompose(Zs,Js,Sn),Sn.x===1&&Sn.y===1&&Sn.z===1?this.matrixWorldInverse.copy(this.matrixWorld).invert():this.matrixWorldInverse.compose(Zs,Js,Sn.set(1,1,1)).invert()}updateWorldMatrix(t,e){super.updateWorldMatrix(t,e),this.matrixWorld.decompose(Zs,Js,Sn),Sn.x===1&&Sn.y===1&&Sn.z===1?this.matrixWorldInverse.copy(this.matrixWorld).invert():this.matrixWorldInverse.compose(Zs,Js,Sn.set(1,1,1)).invert()}clone(){return new this.constructor().copy(this)}}const di=new W,Lu=new Qt,Iu=new Qt;class ln extends Jh{constructor(t=50,e=1,n=.1,r=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=t,this.zoom=1,this.near=n,this.far=r,this.focus=10,this.aspect=e,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(t,e){return super.copy(t,e),this.fov=t.fov,this.zoom=t.zoom,this.near=t.near,this.far=t.far,this.focus=t.focus,this.aspect=t.aspect,this.view=t.view===null?null:Object.assign({},t.view),this.filmGauge=t.filmGauge,this.filmOffset=t.filmOffset,this}setFocalLength(t){const e=.5*this.getFilmHeight()/t;this.fov=Vl*2*Math.atan(e),this.updateProjectionMatrix()}getFocalLength(){const t=Math.tan(io*.5*this.fov);return .5*this.getFilmHeight()/t}getEffectiveFOV(){return Vl*2*Math.atan(Math.tan(io*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(t,e,n){di.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),e.set(di.x,di.y).multiplyScalar(-t/di.z),di.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(di.x,di.y).multiplyScalar(-t/di.z)}getViewSize(t,e){return this.getViewBounds(t,Lu,Iu),e.subVectors(Iu,Lu)}setViewOffset(t,e,n,r,s,a){this.aspect=t/e,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=t,this.view.fullHeight=e,this.view.offsetX=n,this.view.offsetY=r,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const t=this.near;let e=t*Math.tan(io*.5*this.fov)/this.zoom,n=2*e,r=this.aspect*n,s=-.5*r;const a=this.view;if(this.view!==null&&this.view.enabled){const l=a.fullWidth,c=a.fullHeight;s+=a.offsetX*r/l,e-=a.offsetY*n/c,r*=a.width/l,n*=a.height/c}const o=this.filmOffset;o!==0&&(s+=t*o/this.getFilmWidth()),this.projectionMatrix.makePerspective(s,s+r,e,e-n,t,this.far,this.coordinateSystem,this.reversedDepth),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(t){const e=super.toJSON(t);return e.object.fov=this.fov,e.object.zoom=this.zoom,e.object.near=this.near,e.object.far=this.far,e.object.focus=this.focus,e.object.aspect=this.aspect,this.view!==null&&(e.object.view=Object.assign({},this.view)),e.object.filmGauge=this.filmGauge,e.object.filmOffset=this.filmOffset,e}}class jh extends Jh{constructor(t=-1,e=1,n=1,r=-1,s=.1,a=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=t,this.right=e,this.top=n,this.bottom=r,this.near=s,this.far=a,this.updateProjectionMatrix()}copy(t,e){return super.copy(t,e),this.left=t.left,this.right=t.right,this.top=t.top,this.bottom=t.bottom,this.near=t.near,this.far=t.far,this.zoom=t.zoom,this.view=t.view===null?null:Object.assign({},t.view),this}setViewOffset(t,e,n,r,s,a){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=t,this.view.fullHeight=e,this.view.offsetX=n,this.view.offsetY=r,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const t=(this.right-this.left)/(2*this.zoom),e=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,r=(this.top+this.bottom)/2;let s=n-t,a=n+t,o=r+e,l=r-e;if(this.view!==null&&this.view.enabled){const c=(this.right-this.left)/this.view.fullWidth/this.zoom,u=(this.top-this.bottom)/this.view.fullHeight/this.zoom;s+=c*this.view.offsetX,a=s+c*this.view.width,o-=u*this.view.offsetY,l=o-u*this.view.height}this.projectionMatrix.makeOrthographic(s,a,o,l,this.near,this.far,this.coordinateSystem,this.reversedDepth),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(t){const e=super.toJSON(t);return e.object.zoom=this.zoom,e.object.left=this.left,e.object.right=this.right,e.object.top=this.top,e.object.bottom=this.bottom,e.object.near=this.near,e.object.far=this.far,this.view!==null&&(e.object.view=Object.assign({},this.view)),e}}const pr=-90,mr=1;class v_ extends tn{constructor(t,e,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const r=new ln(pr,mr,t,e);r.layers=this.layers,this.add(r);const s=new ln(pr,mr,t,e);s.layers=this.layers,this.add(s);const a=new ln(pr,mr,t,e);a.layers=this.layers,this.add(a);const o=new ln(pr,mr,t,e);o.layers=this.layers,this.add(o);const l=new ln(pr,mr,t,e);l.layers=this.layers,this.add(l);const c=new ln(pr,mr,t,e);c.layers=this.layers,this.add(c)}updateCoordinateSystem(){const t=this.coordinateSystem,e=this.children.concat(),[n,r,s,a,o,l]=e;for(const c of e)this.remove(c);if(t===Rn)n.up.set(0,1,0),n.lookAt(1,0,0),r.up.set(0,1,0),r.lookAt(-1,0,0),s.up.set(0,0,-1),s.lookAt(0,1,0),a.up.set(0,0,1),a.lookAt(0,-1,0),o.up.set(0,1,0),o.lookAt(0,0,1),l.up.set(0,1,0),l.lookAt(0,0,-1);else if(t===Ta)n.up.set(0,-1,0),n.lookAt(-1,0,0),r.up.set(0,-1,0),r.lookAt(1,0,0),s.up.set(0,0,1),s.lookAt(0,1,0),a.up.set(0,0,-1),a.lookAt(0,-1,0),o.up.set(0,-1,0),o.lookAt(0,0,1),l.up.set(0,-1,0),l.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+t);for(const c of e)this.add(c),c.updateMatrixWorld()}update(t,e){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:r}=this;this.coordinateSystem!==t.coordinateSystem&&(this.coordinateSystem=t.coordinateSystem,this.updateCoordinateSystem());const[s,a,o,l,c,u]=this.children,h=t.getRenderTarget(),f=t.getActiveCubeFace(),d=t.getActiveMipmapLevel(),_=t.xr.enabled;t.xr.enabled=!1;const g=n.texture.generateMipmaps;n.texture.generateMipmaps=!1;let p=!1;t.isWebGLRenderer===!0?p=t.state.buffers.depth.getReversed():p=t.reversedDepthBuffer,t.setRenderTarget(n,0,r),p&&t.autoClear===!1&&t.clearDepth(),t.render(e,s),t.setRenderTarget(n,1,r),p&&t.autoClear===!1&&t.clearDepth(),t.render(e,a),t.setRenderTarget(n,2,r),p&&t.autoClear===!1&&t.clearDepth(),t.render(e,o),t.setRenderTarget(n,3,r),p&&t.autoClear===!1&&t.clearDepth(),t.render(e,l),t.setRenderTarget(n,4,r),p&&t.autoClear===!1&&t.clearDepth(),t.render(e,c),n.texture.generateMipmaps=g,t.setRenderTarget(n,5,r),p&&t.autoClear===!1&&t.clearDepth(),t.render(e,u),t.setRenderTarget(h,f,d),t.xr.enabled=_,n.texture.needsPMREMUpdate=!0}}class M_ extends ln{constructor(t=[]){super(),this.isArrayCamera=!0,this.isMultiViewCamera=!1,this.cameras=t}}function Uu(i,t,e,n){const r=S_(n);switch(e){case Bh:return i*t;case zh:return i*t/r.components*r.byteLength;case yc:return i*t/r.components*r.byteLength;case Ir:return i*t*2/r.components*r.byteLength;case Ec:return i*t*2/r.components*r.byteLength;case kh:return i*t*3/r.components*r.byteLength;case xn:return i*t*4/r.components*r.byteLength;case Tc:return i*t*4/r.components*r.byteLength;case la:case ca:return Math.floor((i+3)/4)*Math.floor((t+3)/4)*8;case ua:case fa:return Math.floor((i+3)/4)*Math.floor((t+3)/4)*16;case ul:case hl:return Math.max(i,16)*Math.max(t,8)/4;case cl:case fl:return Math.max(i,8)*Math.max(t,8)/2;case dl:case pl:case _l:case gl:return Math.floor((i+3)/4)*Math.floor((t+3)/4)*8;case ml:case xl:case vl:return Math.floor((i+3)/4)*Math.floor((t+3)/4)*16;case Ml:return Math.floor((i+3)/4)*Math.floor((t+3)/4)*16;case Sl:return Math.floor((i+4)/5)*Math.floor((t+3)/4)*16;case yl:return Math.floor((i+4)/5)*Math.floor((t+4)/5)*16;case El:return Math.floor((i+5)/6)*Math.floor((t+4)/5)*16;case Tl:return Math.floor((i+5)/6)*Math.floor((t+5)/6)*16;case bl:return Math.floor((i+7)/8)*Math.floor((t+4)/5)*16;case Al:return Math.floor((i+7)/8)*Math.floor((t+5)/6)*16;case wl:return Math.floor((i+7)/8)*Math.floor((t+7)/8)*16;case Rl:return Math.floor((i+9)/10)*Math.floor((t+4)/5)*16;case Cl:return Math.floor((i+9)/10)*Math.floor((t+5)/6)*16;case Pl:return Math.floor((i+9)/10)*Math.floor((t+7)/8)*16;case Dl:return Math.floor((i+9)/10)*Math.floor((t+9)/10)*16;case Ll:return Math.floor((i+11)/12)*Math.floor((t+9)/10)*16;case Il:return Math.floor((i+11)/12)*Math.floor((t+11)/12)*16;case Ul:case Nl:case Fl:return Math.ceil(i/4)*Math.ceil(t/4)*16;case Ol:case Bl:return Math.ceil(i/4)*Math.ceil(t/4)*8;case kl:case zl:return Math.ceil(i/4)*Math.ceil(t/4)*16}throw new Error(`Unable to determine texture byte length for ${e} format.`)}function S_(i){switch(i){case cn:case Uh:return{byteLength:1,components:1};case ps:case Nh:case ei:return{byteLength:2,components:1};case Mc:case Sc:return{byteLength:2,components:4};case Un:case vc:case wn:return{byteLength:4,components:1};case Fh:case Oh:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${i}.`)}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:xc}}));typeof window<"u"&&(window.__THREE__?Pt("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=xc);/**
 * @license
 * Copyright 2010-2026 Three.js Authors
 * SPDX-License-Identifier: MIT
 */function Qh(){let i=null,t=!1,e=null,n=null;function r(s,a){e(s,a),n=i.requestAnimationFrame(r)}return{start:function(){t!==!0&&e!==null&&(n=i.requestAnimationFrame(r),t=!0)},stop:function(){i.cancelAnimationFrame(n),t=!1},setAnimationLoop:function(s){e=s},setContext:function(s){i=s}}}function y_(i){const t=new WeakMap;function e(o,l){const c=o.array,u=o.usage,h=c.byteLength,f=i.createBuffer();i.bindBuffer(l,f),i.bufferData(l,c,u),o.onUploadCallback();let d;if(c instanceof Float32Array)d=i.FLOAT;else if(typeof Float16Array<"u"&&c instanceof Float16Array)d=i.HALF_FLOAT;else if(c instanceof Uint16Array)o.isFloat16BufferAttribute?d=i.HALF_FLOAT:d=i.UNSIGNED_SHORT;else if(c instanceof Int16Array)d=i.SHORT;else if(c instanceof Uint32Array)d=i.UNSIGNED_INT;else if(c instanceof Int32Array)d=i.INT;else if(c instanceof Int8Array)d=i.BYTE;else if(c instanceof Uint8Array)d=i.UNSIGNED_BYTE;else if(c instanceof Uint8ClampedArray)d=i.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+c);return{buffer:f,type:d,bytesPerElement:c.BYTES_PER_ELEMENT,version:o.version,size:h}}function n(o,l,c){const u=l.array,h=l.updateRanges;if(i.bindBuffer(c,o),h.length===0)i.bufferSubData(c,0,u);else{h.sort((d,_)=>d.start-_.start);let f=0;for(let d=1;d<h.length;d++){const _=h[f],g=h[d];g.start<=_.start+_.count+1?_.count=Math.max(_.count,g.start+g.count-_.start):(++f,h[f]=g)}h.length=f+1;for(let d=0,_=h.length;d<_;d++){const g=h[d];i.bufferSubData(c,g.start*u.BYTES_PER_ELEMENT,u,g.start,g.count)}l.clearUpdateRanges()}l.onUploadCallback()}function r(o){return o.isInterleavedBufferAttribute&&(o=o.data),t.get(o)}function s(o){o.isInterleavedBufferAttribute&&(o=o.data);const l=t.get(o);l&&(i.deleteBuffer(l.buffer),t.delete(o))}function a(o,l){if(o.isInterleavedBufferAttribute&&(o=o.data),o.isGLBufferAttribute){const u=t.get(o);(!u||u.version<o.version)&&t.set(o,{buffer:o.buffer,type:o.type,bytesPerElement:o.elementSize,version:o.version});return}const c=t.get(o);if(c===void 0)t.set(o,e(o,l));else if(c.version<o.version){if(c.size!==o.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(c.buffer,o,l),c.version=o.version}}return{get:r,remove:s,update:a}}var E_=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,T_=`#ifdef USE_ALPHAHASH
	const float ALPHA_HASH_SCALE = 0.05;
	float hash2D( vec2 value ) {
		return fract( 1.0e4 * sin( 17.0 * value.x + 0.1 * value.y ) * ( 0.1 + abs( sin( 13.0 * value.y + value.x ) ) ) );
	}
	float hash3D( vec3 value ) {
		return hash2D( vec2( hash2D( value.xy ), value.z ) );
	}
	float getAlphaHashThreshold( vec3 position ) {
		float maxDeriv = max(
			length( dFdx( position.xyz ) ),
			length( dFdy( position.xyz ) )
		);
		float pixScale = 1.0 / ( ALPHA_HASH_SCALE * maxDeriv );
		vec2 pixScales = vec2(
			exp2( floor( log2( pixScale ) ) ),
			exp2( ceil( log2( pixScale ) ) )
		);
		vec2 alpha = vec2(
			hash3D( floor( pixScales.x * position.xyz ) ),
			hash3D( floor( pixScales.y * position.xyz ) )
		);
		float lerpFactor = fract( log2( pixScale ) );
		float x = ( 1.0 - lerpFactor ) * alpha.x + lerpFactor * alpha.y;
		float a = min( lerpFactor, 1.0 - lerpFactor );
		vec3 cases = vec3(
			x * x / ( 2.0 * a * ( 1.0 - a ) ),
			( x - 0.5 * a ) / ( 1.0 - a ),
			1.0 - ( ( 1.0 - x ) * ( 1.0 - x ) / ( 2.0 * a * ( 1.0 - a ) ) )
		);
		float threshold = ( x < ( 1.0 - a ) )
			? ( ( x < a ) ? cases.x : cases.y )
			: cases.z;
		return clamp( threshold , 1.0e-6, 1.0 );
	}
#endif`,b_=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,A_=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,w_=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,R_=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,C_=`#ifdef USE_AOMAP
	float ambientOcclusion = ( texture2D( aoMap, vAoMapUv ).r - 1.0 ) * aoMapIntensity + 1.0;
	reflectedLight.indirectDiffuse *= ambientOcclusion;
	#if defined( USE_CLEARCOAT ) 
		clearcoatSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_SHEEN ) 
		sheenSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD )
		float dotNV = saturate( dot( geometryNormal, geometryViewDir ) );
		reflectedLight.indirectSpecular *= computeSpecularOcclusion( dotNV, ambientOcclusion, material.roughness );
	#endif
#endif`,P_=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,D_=`#ifdef USE_BATCHING
	#if ! defined( GL_ANGLE_multi_draw )
	#define gl_DrawID _gl_DrawID
	uniform int _gl_DrawID;
	#endif
	uniform highp sampler2D batchingTexture;
	uniform highp usampler2D batchingIdTexture;
	mat4 getBatchingMatrix( const in float i ) {
		int size = textureSize( batchingTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( batchingTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( batchingTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( batchingTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( batchingTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
	float getIndirectIndex( const in int i ) {
		int size = textureSize( batchingIdTexture, 0 ).x;
		int x = i % size;
		int y = i / size;
		return float( texelFetch( batchingIdTexture, ivec2( x, y ), 0 ).r );
	}
#endif
#ifdef USE_BATCHING_COLOR
	uniform sampler2D batchingColorTexture;
	vec4 getBatchingColor( const in float i ) {
		int size = textureSize( batchingColorTexture, 0 ).x;
		int j = int( i );
		int x = j % size;
		int y = j / size;
		return texelFetch( batchingColorTexture, ivec2( x, y ), 0 );
	}
#endif`,L_=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,I_=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,U_=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,N_=`float G_BlinnPhong_Implicit( ) {
	return 0.25;
}
float D_BlinnPhong( const in float shininess, const in float dotNH ) {
	return RECIPROCAL_PI * ( shininess * 0.5 + 1.0 ) * pow( dotNH, shininess );
}
vec3 BRDF_BlinnPhong( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in vec3 specularColor, const in float shininess ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( specularColor, 1.0, dotVH );
	float G = G_BlinnPhong_Implicit( );
	float D = D_BlinnPhong( shininess, dotNH );
	return F * ( G * D );
} // validated`,F_=`#ifdef USE_IRIDESCENCE
	const mat3 XYZ_TO_REC709 = mat3(
		 3.2404542, -0.9692660,  0.0556434,
		-1.5371385,  1.8760108, -0.2040259,
		-0.4985314,  0.0415560,  1.0572252
	);
	vec3 Fresnel0ToIor( vec3 fresnel0 ) {
		vec3 sqrtF0 = sqrt( fresnel0 );
		return ( vec3( 1.0 ) + sqrtF0 ) / ( vec3( 1.0 ) - sqrtF0 );
	}
	vec3 IorToFresnel0( vec3 transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - vec3( incidentIor ) ) / ( transmittedIor + vec3( incidentIor ) ) );
	}
	float IorToFresnel0( float transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - incidentIor ) / ( transmittedIor + incidentIor ));
	}
	vec3 evalSensitivity( float OPD, vec3 shift ) {
		float phase = 2.0 * PI * OPD * 1.0e-9;
		vec3 val = vec3( 5.4856e-13, 4.4201e-13, 5.2481e-13 );
		vec3 pos = vec3( 1.6810e+06, 1.7953e+06, 2.2084e+06 );
		vec3 var = vec3( 4.3278e+09, 9.3046e+09, 6.6121e+09 );
		vec3 xyz = val * sqrt( 2.0 * PI * var ) * cos( pos * phase + shift ) * exp( - pow2( phase ) * var );
		xyz.x += 9.7470e-14 * sqrt( 2.0 * PI * 4.5282e+09 ) * cos( 2.2399e+06 * phase + shift[ 0 ] ) * exp( - 4.5282e+09 * pow2( phase ) );
		xyz /= 1.0685e-7;
		vec3 rgb = XYZ_TO_REC709 * xyz;
		return rgb;
	}
	vec3 evalIridescence( float outsideIOR, float eta2, float cosTheta1, float thinFilmThickness, vec3 baseF0 ) {
		vec3 I;
		float iridescenceIOR = mix( outsideIOR, eta2, smoothstep( 0.0, 0.03, thinFilmThickness ) );
		float sinTheta2Sq = pow2( outsideIOR / iridescenceIOR ) * ( 1.0 - pow2( cosTheta1 ) );
		float cosTheta2Sq = 1.0 - sinTheta2Sq;
		if ( cosTheta2Sq < 0.0 ) {
			return vec3( 1.0 );
		}
		float cosTheta2 = sqrt( cosTheta2Sq );
		float R0 = IorToFresnel0( iridescenceIOR, outsideIOR );
		float R12 = F_Schlick( R0, 1.0, cosTheta1 );
		float T121 = 1.0 - R12;
		float phi12 = 0.0;
		if ( iridescenceIOR < outsideIOR ) phi12 = PI;
		float phi21 = PI - phi12;
		vec3 baseIOR = Fresnel0ToIor( clamp( baseF0, 0.0, 0.9999 ) );		vec3 R1 = IorToFresnel0( baseIOR, iridescenceIOR );
		vec3 R23 = F_Schlick( R1, 1.0, cosTheta2 );
		vec3 phi23 = vec3( 0.0 );
		if ( baseIOR[ 0 ] < iridescenceIOR ) phi23[ 0 ] = PI;
		if ( baseIOR[ 1 ] < iridescenceIOR ) phi23[ 1 ] = PI;
		if ( baseIOR[ 2 ] < iridescenceIOR ) phi23[ 2 ] = PI;
		float OPD = 2.0 * iridescenceIOR * thinFilmThickness * cosTheta2;
		vec3 phi = vec3( phi21 ) + phi23;
		vec3 R123 = clamp( R12 * R23, 1e-5, 0.9999 );
		vec3 r123 = sqrt( R123 );
		vec3 Rs = pow2( T121 ) * R23 / ( vec3( 1.0 ) - R123 );
		vec3 C0 = R12 + Rs;
		I = C0;
		vec3 Cm = Rs - T121;
		for ( int m = 1; m <= 2; ++ m ) {
			Cm *= r123;
			vec3 Sm = 2.0 * evalSensitivity( float( m ) * OPD, float( m ) * phi );
			I += Cm * Sm;
		}
		return max( I, vec3( 0.0 ) );
	}
#endif`,O_=`#ifdef USE_BUMPMAP
	uniform sampler2D bumpMap;
	uniform float bumpScale;
	vec2 dHdxy_fwd() {
		vec2 dSTdx = dFdx( vBumpMapUv );
		vec2 dSTdy = dFdy( vBumpMapUv );
		float Hll = bumpScale * texture2D( bumpMap, vBumpMapUv ).x;
		float dBx = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdx ).x - Hll;
		float dBy = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdy ).x - Hll;
		return vec2( dBx, dBy );
	}
	vec3 perturbNormalArb( vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDirection ) {
		vec3 vSigmaX = normalize( dFdx( surf_pos.xyz ) );
		vec3 vSigmaY = normalize( dFdy( surf_pos.xyz ) );
		vec3 vN = surf_norm;
		vec3 R1 = cross( vSigmaY, vN );
		vec3 R2 = cross( vN, vSigmaX );
		float fDet = dot( vSigmaX, R1 ) * faceDirection;
		vec3 vGrad = sign( fDet ) * ( dHdxy.x * R1 + dHdxy.y * R2 );
		return normalize( abs( fDet ) * surf_norm - vGrad );
	}
#endif`,B_=`#if NUM_CLIPPING_PLANES > 0
	vec4 plane;
	#ifdef ALPHA_TO_COVERAGE
		float distanceToPlane, distanceGradient;
		float clipOpacity = 1.0;
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
			distanceGradient = fwidth( distanceToPlane ) / 2.0;
			clipOpacity *= smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			if ( clipOpacity == 0.0 ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			float unionClipOpacity = 1.0;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
				distanceGradient = fwidth( distanceToPlane ) / 2.0;
				unionClipOpacity *= 1.0 - smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			}
			#pragma unroll_loop_end
			clipOpacity *= 1.0 - unionClipOpacity;
		#endif
		diffuseColor.a *= clipOpacity;
		if ( diffuseColor.a == 0.0 ) discard;
	#else
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			if ( dot( vClipPosition, plane.xyz ) > plane.w ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			bool clipped = true;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				clipped = ( dot( vClipPosition, plane.xyz ) > plane.w ) && clipped;
			}
			#pragma unroll_loop_end
			if ( clipped ) discard;
		#endif
	#endif
#endif`,k_=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,z_=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,V_=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,G_=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#endif`,H_=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#endif`,W_=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec4 vColor;
#endif`,X_=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	vColor = vec4( 1.0 );
#endif
#ifdef USE_COLOR_ALPHA
	vColor *= color;
#elif defined( USE_COLOR )
	vColor.rgb *= color;
#endif
#ifdef USE_INSTANCING_COLOR
	vColor.rgb *= instanceColor.rgb;
#endif
#ifdef USE_BATCHING_COLOR
	vColor *= getBatchingColor( getIndirectIndex( gl_DrawID ) );
#endif`,q_=`#define PI 3.141592653589793
#define PI2 6.283185307179586
#define PI_HALF 1.5707963267948966
#define RECIPROCAL_PI 0.3183098861837907
#define RECIPROCAL_PI2 0.15915494309189535
#define EPSILON 1e-6
#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
#define whiteComplement( a ) ( 1.0 - saturate( a ) )
float pow2( const in float x ) { return x*x; }
vec3 pow2( const in vec3 x ) { return x*x; }
float pow3( const in float x ) { return x*x*x; }
float pow4( const in float x ) { float x2 = x*x; return x2*x2; }
float max3( const in vec3 v ) { return max( max( v.x, v.y ), v.z ); }
float average( const in vec3 v ) { return dot( v, vec3( 0.3333333 ) ); }
highp float rand( const in vec2 uv ) {
	const highp float a = 12.9898, b = 78.233, c = 43758.5453;
	highp float dt = dot( uv.xy, vec2( a,b ) ), sn = mod( dt, PI );
	return fract( sin( sn ) * c );
}
#ifdef HIGH_PRECISION
	float precisionSafeLength( vec3 v ) { return length( v ); }
#else
	float precisionSafeLength( vec3 v ) {
		float maxComponent = max3( abs( v ) );
		return length( v / maxComponent ) * maxComponent;
	}
#endif
struct IncidentLight {
	vec3 color;
	vec3 direction;
	bool visible;
};
struct ReflectedLight {
	vec3 directDiffuse;
	vec3 directSpecular;
	vec3 indirectDiffuse;
	vec3 indirectSpecular;
};
#ifdef USE_ALPHAHASH
	varying vec3 vPosition;
#endif
vec3 transformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );
}
vec3 inverseTransformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( vec4( dir, 0.0 ) * matrix ).xyz );
}
bool isPerspectiveMatrix( mat4 m ) {
	return m[ 2 ][ 3 ] == - 1.0;
}
vec2 equirectUv( in vec3 dir ) {
	float u = atan( dir.z, dir.x ) * RECIPROCAL_PI2 + 0.5;
	float v = asin( clamp( dir.y, - 1.0, 1.0 ) ) * RECIPROCAL_PI + 0.5;
	return vec2( u, v );
}
vec3 BRDF_Lambert( const in vec3 diffuseColor ) {
	return RECIPROCAL_PI * diffuseColor;
}
vec3 F_Schlick( const in vec3 f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
}
float F_Schlick( const in float f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
} // validated`,Y_=`#ifdef ENVMAP_TYPE_CUBE_UV
	#define cubeUV_minMipLevel 4.0
	#define cubeUV_minTileSize 16.0
	float getFace( vec3 direction ) {
		vec3 absDirection = abs( direction );
		float face = - 1.0;
		if ( absDirection.x > absDirection.z ) {
			if ( absDirection.x > absDirection.y )
				face = direction.x > 0.0 ? 0.0 : 3.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		} else {
			if ( absDirection.z > absDirection.y )
				face = direction.z > 0.0 ? 2.0 : 5.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		}
		return face;
	}
	vec2 getUV( vec3 direction, float face ) {
		vec2 uv;
		if ( face == 0.0 ) {
			uv = vec2( direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 1.0 ) {
			uv = vec2( - direction.x, - direction.z ) / abs( direction.y );
		} else if ( face == 2.0 ) {
			uv = vec2( - direction.x, direction.y ) / abs( direction.z );
		} else if ( face == 3.0 ) {
			uv = vec2( - direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 4.0 ) {
			uv = vec2( - direction.x, direction.z ) / abs( direction.y );
		} else {
			uv = vec2( direction.x, direction.y ) / abs( direction.z );
		}
		return 0.5 * ( uv + 1.0 );
	}
	vec3 bilinearCubeUV( sampler2D envMap, vec3 direction, float mipInt ) {
		float face = getFace( direction );
		float filterInt = max( cubeUV_minMipLevel - mipInt, 0.0 );
		mipInt = max( mipInt, cubeUV_minMipLevel );
		float faceSize = exp2( mipInt );
		highp vec2 uv = getUV( direction, face ) * ( faceSize - 2.0 ) + 1.0;
		if ( face > 2.0 ) {
			uv.y += faceSize;
			face -= 3.0;
		}
		uv.x += face * faceSize;
		uv.x += filterInt * 3.0 * cubeUV_minTileSize;
		uv.y += 4.0 * ( exp2( CUBEUV_MAX_MIP ) - faceSize );
		uv.x *= CUBEUV_TEXEL_WIDTH;
		uv.y *= CUBEUV_TEXEL_HEIGHT;
		#ifdef texture2DGradEXT
			return texture2DGradEXT( envMap, uv, vec2( 0.0 ), vec2( 0.0 ) ).rgb;
		#else
			return texture2D( envMap, uv ).rgb;
		#endif
	}
	#define cubeUV_r0 1.0
	#define cubeUV_m0 - 2.0
	#define cubeUV_r1 0.8
	#define cubeUV_m1 - 1.0
	#define cubeUV_r4 0.4
	#define cubeUV_m4 2.0
	#define cubeUV_r5 0.305
	#define cubeUV_m5 3.0
	#define cubeUV_r6 0.21
	#define cubeUV_m6 4.0
	float roughnessToMip( float roughness ) {
		float mip = 0.0;
		if ( roughness >= cubeUV_r1 ) {
			mip = ( cubeUV_r0 - roughness ) * ( cubeUV_m1 - cubeUV_m0 ) / ( cubeUV_r0 - cubeUV_r1 ) + cubeUV_m0;
		} else if ( roughness >= cubeUV_r4 ) {
			mip = ( cubeUV_r1 - roughness ) * ( cubeUV_m4 - cubeUV_m1 ) / ( cubeUV_r1 - cubeUV_r4 ) + cubeUV_m1;
		} else if ( roughness >= cubeUV_r5 ) {
			mip = ( cubeUV_r4 - roughness ) * ( cubeUV_m5 - cubeUV_m4 ) / ( cubeUV_r4 - cubeUV_r5 ) + cubeUV_m4;
		} else if ( roughness >= cubeUV_r6 ) {
			mip = ( cubeUV_r5 - roughness ) * ( cubeUV_m6 - cubeUV_m5 ) / ( cubeUV_r5 - cubeUV_r6 ) + cubeUV_m5;
		} else {
			mip = - 2.0 * log2( 1.16 * roughness );		}
		return mip;
	}
	vec4 textureCubeUV( sampler2D envMap, vec3 sampleDir, float roughness ) {
		float mip = clamp( roughnessToMip( roughness ), cubeUV_m0, CUBEUV_MAX_MIP );
		float mipF = fract( mip );
		float mipInt = floor( mip );
		vec3 color0 = bilinearCubeUV( envMap, sampleDir, mipInt );
		if ( mipF == 0.0 ) {
			return vec4( color0, 1.0 );
		} else {
			vec3 color1 = bilinearCubeUV( envMap, sampleDir, mipInt + 1.0 );
			return vec4( mix( color0, color1, mipF ), 1.0 );
		}
	}
#endif`,$_=`vec3 transformedNormal = objectNormal;
#ifdef USE_TANGENT
	vec3 transformedTangent = objectTangent;
#endif
#ifdef USE_BATCHING
	mat3 bm = mat3( batchingMatrix );
	transformedNormal /= vec3( dot( bm[ 0 ], bm[ 0 ] ), dot( bm[ 1 ], bm[ 1 ] ), dot( bm[ 2 ], bm[ 2 ] ) );
	transformedNormal = bm * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = bm * transformedTangent;
	#endif
#endif
#ifdef USE_INSTANCING
	mat3 im = mat3( instanceMatrix );
	transformedNormal /= vec3( dot( im[ 0 ], im[ 0 ] ), dot( im[ 1 ], im[ 1 ] ), dot( im[ 2 ], im[ 2 ] ) );
	transformedNormal = im * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = im * transformedTangent;
	#endif
#endif
transformedNormal = normalMatrix * transformedNormal;
#ifdef FLIP_SIDED
	transformedNormal = - transformedNormal;
#endif
#ifdef USE_TANGENT
	transformedTangent = ( modelViewMatrix * vec4( transformedTangent, 0.0 ) ).xyz;
	#ifdef FLIP_SIDED
		transformedTangent = - transformedTangent;
	#endif
#endif`,K_=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,Z_=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,J_=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,j_=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,Q_="gl_FragColor = linearToOutputTexel( gl_FragColor );",tg=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,eg=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vec3 cameraToFrag;
		if ( isOrthographic ) {
			cameraToFrag = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToFrag = normalize( vWorldPosition - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vec3 reflectVec = reflect( cameraToFrag, worldNormal );
		#else
			vec3 reflectVec = refract( cameraToFrag, worldNormal, refractionRatio );
		#endif
	#else
		vec3 reflectVec = vReflect;
	#endif
	#ifdef ENVMAP_TYPE_CUBE
		vec4 envColor = textureCube( envMap, envMapRotation * vec3( flipEnvMap * reflectVec.x, reflectVec.yz ) );
		#ifdef ENVMAP_BLENDING_MULTIPLY
			outgoingLight = mix( outgoingLight, outgoingLight * envColor.xyz, specularStrength * reflectivity );
		#elif defined( ENVMAP_BLENDING_MIX )
			outgoingLight = mix( outgoingLight, envColor.xyz, specularStrength * reflectivity );
		#elif defined( ENVMAP_BLENDING_ADD )
			outgoingLight += envColor.xyz * specularStrength * reflectivity;
		#endif
	#endif
#endif`,ng=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
#endif`,ig=`#ifdef USE_ENVMAP
	uniform float reflectivity;
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		varying vec3 vWorldPosition;
		uniform float refractionRatio;
	#else
		varying vec3 vReflect;
	#endif
#endif`,rg=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,sg=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vWorldPosition = worldPosition.xyz;
	#else
		vec3 cameraToVertex;
		if ( isOrthographic ) {
			cameraToVertex = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToVertex = normalize( worldPosition.xyz - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vReflect = reflect( cameraToVertex, worldNormal );
		#else
			vReflect = refract( cameraToVertex, worldNormal, refractionRatio );
		#endif
	#endif
#endif`,ag=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,og=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,lg=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,cg=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,ug=`#ifdef USE_GRADIENTMAP
	uniform sampler2D gradientMap;
#endif
vec3 getGradientIrradiance( vec3 normal, vec3 lightDirection ) {
	float dotNL = dot( normal, lightDirection );
	vec2 coord = vec2( dotNL * 0.5 + 0.5, 0.0 );
	#ifdef USE_GRADIENTMAP
		return vec3( texture2D( gradientMap, coord ).r );
	#else
		vec2 fw = fwidth( coord ) * 0.5;
		return mix( vec3( 0.7 ), vec3( 1.0 ), smoothstep( 0.7 - fw.x, 0.7 + fw.x, coord.x ) );
	#endif
}`,fg=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,hg=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,dg=`varying vec3 vViewPosition;
struct LambertMaterial {
	vec3 diffuseColor;
	float specularStrength;
};
void RE_Direct_Lambert( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Lambert( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Lambert
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,pg=`uniform bool receiveShadow;
uniform vec3 ambientLightColor;
#if defined( USE_LIGHT_PROBES )
	uniform vec3 lightProbe[ 9 ];
#endif
vec3 shGetIrradianceAt( in vec3 normal, in vec3 shCoefficients[ 9 ] ) {
	float x = normal.x, y = normal.y, z = normal.z;
	vec3 result = shCoefficients[ 0 ] * 0.886227;
	result += shCoefficients[ 1 ] * 2.0 * 0.511664 * y;
	result += shCoefficients[ 2 ] * 2.0 * 0.511664 * z;
	result += shCoefficients[ 3 ] * 2.0 * 0.511664 * x;
	result += shCoefficients[ 4 ] * 2.0 * 0.429043 * x * y;
	result += shCoefficients[ 5 ] * 2.0 * 0.429043 * y * z;
	result += shCoefficients[ 6 ] * ( 0.743125 * z * z - 0.247708 );
	result += shCoefficients[ 7 ] * 2.0 * 0.429043 * x * z;
	result += shCoefficients[ 8 ] * 0.429043 * ( x * x - y * y );
	return result;
}
vec3 getLightProbeIrradiance( const in vec3 lightProbe[ 9 ], const in vec3 normal ) {
	vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
	vec3 irradiance = shGetIrradianceAt( worldNormal, lightProbe );
	return irradiance;
}
vec3 getAmbientLightIrradiance( const in vec3 ambientLightColor ) {
	vec3 irradiance = ambientLightColor;
	return irradiance;
}
float getDistanceAttenuation( const in float lightDistance, const in float cutoffDistance, const in float decayExponent ) {
	float distanceFalloff = 1.0 / max( pow( lightDistance, decayExponent ), 0.01 );
	if ( cutoffDistance > 0.0 ) {
		distanceFalloff *= pow2( saturate( 1.0 - pow4( lightDistance / cutoffDistance ) ) );
	}
	return distanceFalloff;
}
float getSpotAttenuation( const in float coneCosine, const in float penumbraCosine, const in float angleCosine ) {
	return smoothstep( coneCosine, penumbraCosine, angleCosine );
}
#if NUM_DIR_LIGHTS > 0
	struct DirectionalLight {
		vec3 direction;
		vec3 color;
	};
	uniform DirectionalLight directionalLights[ NUM_DIR_LIGHTS ];
	void getDirectionalLightInfo( const in DirectionalLight directionalLight, out IncidentLight light ) {
		light.color = directionalLight.color;
		light.direction = directionalLight.direction;
		light.visible = true;
	}
#endif
#if NUM_POINT_LIGHTS > 0
	struct PointLight {
		vec3 position;
		vec3 color;
		float distance;
		float decay;
	};
	uniform PointLight pointLights[ NUM_POINT_LIGHTS ];
	void getPointLightInfo( const in PointLight pointLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = pointLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float lightDistance = length( lVector );
		light.color = pointLight.color;
		light.color *= getDistanceAttenuation( lightDistance, pointLight.distance, pointLight.decay );
		light.visible = ( light.color != vec3( 0.0 ) );
	}
#endif
#if NUM_SPOT_LIGHTS > 0
	struct SpotLight {
		vec3 position;
		vec3 direction;
		vec3 color;
		float distance;
		float decay;
		float coneCos;
		float penumbraCos;
	};
	uniform SpotLight spotLights[ NUM_SPOT_LIGHTS ];
	void getSpotLightInfo( const in SpotLight spotLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = spotLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float angleCos = dot( light.direction, spotLight.direction );
		float spotAttenuation = getSpotAttenuation( spotLight.coneCos, spotLight.penumbraCos, angleCos );
		if ( spotAttenuation > 0.0 ) {
			float lightDistance = length( lVector );
			light.color = spotLight.color * spotAttenuation;
			light.color *= getDistanceAttenuation( lightDistance, spotLight.distance, spotLight.decay );
			light.visible = ( light.color != vec3( 0.0 ) );
		} else {
			light.color = vec3( 0.0 );
			light.visible = false;
		}
	}
#endif
#if NUM_RECT_AREA_LIGHTS > 0
	struct RectAreaLight {
		vec3 color;
		vec3 position;
		vec3 halfWidth;
		vec3 halfHeight;
	};
	uniform sampler2D ltc_1;	uniform sampler2D ltc_2;
	uniform RectAreaLight rectAreaLights[ NUM_RECT_AREA_LIGHTS ];
#endif
#if NUM_HEMI_LIGHTS > 0
	struct HemisphereLight {
		vec3 direction;
		vec3 skyColor;
		vec3 groundColor;
	};
	uniform HemisphereLight hemisphereLights[ NUM_HEMI_LIGHTS ];
	vec3 getHemisphereLightIrradiance( const in HemisphereLight hemiLight, const in vec3 normal ) {
		float dotNL = dot( normal, hemiLight.direction );
		float hemiDiffuseWeight = 0.5 * dotNL + 0.5;
		vec3 irradiance = mix( hemiLight.groundColor, hemiLight.skyColor, hemiDiffuseWeight );
		return irradiance;
	}
#endif`,mg=`#ifdef USE_ENVMAP
	vec3 getIBLIrradiance( const in vec3 normal ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * worldNormal, 1.0 );
			return PI * envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 reflectVec = reflect( - viewDir, normal );
			reflectVec = normalize( mix( reflectVec, normal, pow4( roughness ) ) );
			reflectVec = inverseTransformDirection( reflectVec, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * reflectVec, roughness );
			return envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	#ifdef USE_ANISOTROPY
		vec3 getIBLAnisotropyRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness, const in vec3 bitangent, const in float anisotropy ) {
			#ifdef ENVMAP_TYPE_CUBE_UV
				vec3 bentNormal = cross( bitangent, viewDir );
				bentNormal = normalize( cross( bentNormal, bitangent ) );
				bentNormal = normalize( mix( bentNormal, normal, pow2( pow2( 1.0 - anisotropy * ( 1.0 - roughness ) ) ) ) );
				return getIBLRadiance( viewDir, bentNormal, roughness );
			#else
				return vec3( 0.0 );
			#endif
		}
	#endif
#endif`,_g=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,gg=`varying vec3 vViewPosition;
struct ToonMaterial {
	vec3 diffuseColor;
};
void RE_Direct_Toon( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 irradiance = getGradientIrradiance( geometryNormal, directLight.direction ) * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Toon( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Toon
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,xg=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,vg=`varying vec3 vViewPosition;
struct BlinnPhongMaterial {
	vec3 diffuseColor;
	vec3 specularColor;
	float specularShininess;
	float specularStrength;
};
void RE_Direct_BlinnPhong( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
	reflectedLight.directSpecular += irradiance * BRDF_BlinnPhong( directLight.direction, geometryViewDir, geometryNormal, material.specularColor, material.specularShininess ) * material.specularStrength;
}
void RE_IndirectDiffuse_BlinnPhong( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_BlinnPhong
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,Mg=`PhysicalMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.diffuseContribution = diffuseColor.rgb * ( 1.0 - metalnessFactor );
material.metalness = metalnessFactor;
vec3 dxy = max( abs( dFdx( nonPerturbedNormal ) ), abs( dFdy( nonPerturbedNormal ) ) );
float geometryRoughness = max( max( dxy.x, dxy.y ), dxy.z );
material.roughness = max( roughnessFactor, 0.0525 );material.roughness += geometryRoughness;
material.roughness = min( material.roughness, 1.0 );
#ifdef IOR
	material.ior = ior;
	#ifdef USE_SPECULAR
		float specularIntensityFactor = specularIntensity;
		vec3 specularColorFactor = specularColor;
		#ifdef USE_SPECULAR_COLORMAP
			specularColorFactor *= texture2D( specularColorMap, vSpecularColorMapUv ).rgb;
		#endif
		#ifdef USE_SPECULAR_INTENSITYMAP
			specularIntensityFactor *= texture2D( specularIntensityMap, vSpecularIntensityMapUv ).a;
		#endif
		material.specularF90 = mix( specularIntensityFactor, 1.0, metalnessFactor );
	#else
		float specularIntensityFactor = 1.0;
		vec3 specularColorFactor = vec3( 1.0 );
		material.specularF90 = 1.0;
	#endif
	material.specularColor = min( pow2( ( material.ior - 1.0 ) / ( material.ior + 1.0 ) ) * specularColorFactor, vec3( 1.0 ) ) * specularIntensityFactor;
	material.specularColorBlended = mix( material.specularColor, diffuseColor.rgb, metalnessFactor );
#else
	material.specularColor = vec3( 0.04 );
	material.specularColorBlended = mix( material.specularColor, diffuseColor.rgb, metalnessFactor );
	material.specularF90 = 1.0;
#endif
#ifdef USE_CLEARCOAT
	material.clearcoat = clearcoat;
	material.clearcoatRoughness = clearcoatRoughness;
	material.clearcoatF0 = vec3( 0.04 );
	material.clearcoatF90 = 1.0;
	#ifdef USE_CLEARCOATMAP
		material.clearcoat *= texture2D( clearcoatMap, vClearcoatMapUv ).x;
	#endif
	#ifdef USE_CLEARCOAT_ROUGHNESSMAP
		material.clearcoatRoughness *= texture2D( clearcoatRoughnessMap, vClearcoatRoughnessMapUv ).y;
	#endif
	material.clearcoat = saturate( material.clearcoat );	material.clearcoatRoughness = max( material.clearcoatRoughness, 0.0525 );
	material.clearcoatRoughness += geometryRoughness;
	material.clearcoatRoughness = min( material.clearcoatRoughness, 1.0 );
#endif
#ifdef USE_DISPERSION
	material.dispersion = dispersion;
#endif
#ifdef USE_IRIDESCENCE
	material.iridescence = iridescence;
	material.iridescenceIOR = iridescenceIOR;
	#ifdef USE_IRIDESCENCEMAP
		material.iridescence *= texture2D( iridescenceMap, vIridescenceMapUv ).r;
	#endif
	#ifdef USE_IRIDESCENCE_THICKNESSMAP
		material.iridescenceThickness = (iridescenceThicknessMaximum - iridescenceThicknessMinimum) * texture2D( iridescenceThicknessMap, vIridescenceThicknessMapUv ).g + iridescenceThicknessMinimum;
	#else
		material.iridescenceThickness = iridescenceThicknessMaximum;
	#endif
#endif
#ifdef USE_SHEEN
	material.sheenColor = sheenColor;
	#ifdef USE_SHEEN_COLORMAP
		material.sheenColor *= texture2D( sheenColorMap, vSheenColorMapUv ).rgb;
	#endif
	material.sheenRoughness = clamp( sheenRoughness, 0.0001, 1.0 );
	#ifdef USE_SHEEN_ROUGHNESSMAP
		material.sheenRoughness *= texture2D( sheenRoughnessMap, vSheenRoughnessMapUv ).a;
	#endif
#endif
#ifdef USE_ANISOTROPY
	#ifdef USE_ANISOTROPYMAP
		mat2 anisotropyMat = mat2( anisotropyVector.x, anisotropyVector.y, - anisotropyVector.y, anisotropyVector.x );
		vec3 anisotropyPolar = texture2D( anisotropyMap, vAnisotropyMapUv ).rgb;
		vec2 anisotropyV = anisotropyMat * normalize( 2.0 * anisotropyPolar.rg - vec2( 1.0 ) ) * anisotropyPolar.b;
	#else
		vec2 anisotropyV = anisotropyVector;
	#endif
	material.anisotropy = length( anisotropyV );
	if( material.anisotropy == 0.0 ) {
		anisotropyV = vec2( 1.0, 0.0 );
	} else {
		anisotropyV /= material.anisotropy;
		material.anisotropy = saturate( material.anisotropy );
	}
	material.alphaT = mix( pow2( material.roughness ), 1.0, pow2( material.anisotropy ) );
	material.anisotropyT = tbn[ 0 ] * anisotropyV.x + tbn[ 1 ] * anisotropyV.y;
	material.anisotropyB = tbn[ 1 ] * anisotropyV.x - tbn[ 0 ] * anisotropyV.y;
#endif`,Sg=`uniform sampler2D dfgLUT;
struct PhysicalMaterial {
	vec3 diffuseColor;
	vec3 diffuseContribution;
	vec3 specularColor;
	vec3 specularColorBlended;
	float roughness;
	float metalness;
	float specularF90;
	float dispersion;
	#ifdef USE_CLEARCOAT
		float clearcoat;
		float clearcoatRoughness;
		vec3 clearcoatF0;
		float clearcoatF90;
	#endif
	#ifdef USE_IRIDESCENCE
		float iridescence;
		float iridescenceIOR;
		float iridescenceThickness;
		vec3 iridescenceFresnel;
		vec3 iridescenceF0;
		vec3 iridescenceFresnelDielectric;
		vec3 iridescenceFresnelMetallic;
	#endif
	#ifdef USE_SHEEN
		vec3 sheenColor;
		float sheenRoughness;
	#endif
	#ifdef IOR
		float ior;
	#endif
	#ifdef USE_TRANSMISSION
		float transmission;
		float transmissionAlpha;
		float thickness;
		float attenuationDistance;
		vec3 attenuationColor;
	#endif
	#ifdef USE_ANISOTROPY
		float anisotropy;
		float alphaT;
		vec3 anisotropyT;
		vec3 anisotropyB;
	#endif
};
vec3 clearcoatSpecularDirect = vec3( 0.0 );
vec3 clearcoatSpecularIndirect = vec3( 0.0 );
vec3 sheenSpecularDirect = vec3( 0.0 );
vec3 sheenSpecularIndirect = vec3(0.0 );
vec3 Schlick_to_F0( const in vec3 f, const in float f90, const in float dotVH ) {
    float x = clamp( 1.0 - dotVH, 0.0, 1.0 );
    float x2 = x * x;
    float x5 = clamp( x * x2 * x2, 0.0, 0.9999 );
    return ( f - vec3( f90 ) * x5 ) / ( 1.0 - x5 );
}
float V_GGX_SmithCorrelated( const in float alpha, const in float dotNL, const in float dotNV ) {
	float a2 = pow2( alpha );
	float gv = dotNL * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNV ) );
	float gl = dotNV * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNL ) );
	return 0.5 / max( gv + gl, EPSILON );
}
float D_GGX( const in float alpha, const in float dotNH ) {
	float a2 = pow2( alpha );
	float denom = pow2( dotNH ) * ( a2 - 1.0 ) + 1.0;
	return RECIPROCAL_PI * a2 / pow2( denom );
}
#ifdef USE_ANISOTROPY
	float V_GGX_SmithCorrelated_Anisotropic( const in float alphaT, const in float alphaB, const in float dotTV, const in float dotBV, const in float dotTL, const in float dotBL, const in float dotNV, const in float dotNL ) {
		float gv = dotNL * length( vec3( alphaT * dotTV, alphaB * dotBV, dotNV ) );
		float gl = dotNV * length( vec3( alphaT * dotTL, alphaB * dotBL, dotNL ) );
		float v = 0.5 / ( gv + gl );
		return v;
	}
	float D_GGX_Anisotropic( const in float alphaT, const in float alphaB, const in float dotNH, const in float dotTH, const in float dotBH ) {
		float a2 = alphaT * alphaB;
		highp vec3 v = vec3( alphaB * dotTH, alphaT * dotBH, a2 * dotNH );
		highp float v2 = dot( v, v );
		float w2 = a2 / v2;
		return RECIPROCAL_PI * a2 * pow2 ( w2 );
	}
#endif
#ifdef USE_CLEARCOAT
	vec3 BRDF_GGX_Clearcoat( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material) {
		vec3 f0 = material.clearcoatF0;
		float f90 = material.clearcoatF90;
		float roughness = material.clearcoatRoughness;
		float alpha = pow2( roughness );
		vec3 halfDir = normalize( lightDir + viewDir );
		float dotNL = saturate( dot( normal, lightDir ) );
		float dotNV = saturate( dot( normal, viewDir ) );
		float dotNH = saturate( dot( normal, halfDir ) );
		float dotVH = saturate( dot( viewDir, halfDir ) );
		vec3 F = F_Schlick( f0, f90, dotVH );
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
		return F * ( V * D );
	}
#endif
vec3 BRDF_GGX( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 f0 = material.specularColorBlended;
	float f90 = material.specularF90;
	float roughness = material.roughness;
	float alpha = pow2( roughness );
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( f0, f90, dotVH );
	#ifdef USE_IRIDESCENCE
		F = mix( F, material.iridescenceFresnel, material.iridescence );
	#endif
	#ifdef USE_ANISOTROPY
		float dotTL = dot( material.anisotropyT, lightDir );
		float dotTV = dot( material.anisotropyT, viewDir );
		float dotTH = dot( material.anisotropyT, halfDir );
		float dotBL = dot( material.anisotropyB, lightDir );
		float dotBV = dot( material.anisotropyB, viewDir );
		float dotBH = dot( material.anisotropyB, halfDir );
		float V = V_GGX_SmithCorrelated_Anisotropic( material.alphaT, alpha, dotTV, dotBV, dotTL, dotBL, dotNV, dotNL );
		float D = D_GGX_Anisotropic( material.alphaT, alpha, dotNH, dotTH, dotBH );
	#else
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
	#endif
	return F * ( V * D );
}
vec2 LTC_Uv( const in vec3 N, const in vec3 V, const in float roughness ) {
	const float LUT_SIZE = 64.0;
	const float LUT_SCALE = ( LUT_SIZE - 1.0 ) / LUT_SIZE;
	const float LUT_BIAS = 0.5 / LUT_SIZE;
	float dotNV = saturate( dot( N, V ) );
	vec2 uv = vec2( roughness, sqrt( 1.0 - dotNV ) );
	uv = uv * LUT_SCALE + LUT_BIAS;
	return uv;
}
float LTC_ClippedSphereFormFactor( const in vec3 f ) {
	float l = length( f );
	return max( ( l * l + f.z ) / ( l + 1.0 ), 0.0 );
}
vec3 LTC_EdgeVectorFormFactor( const in vec3 v1, const in vec3 v2 ) {
	float x = dot( v1, v2 );
	float y = abs( x );
	float a = 0.8543985 + ( 0.4965155 + 0.0145206 * y ) * y;
	float b = 3.4175940 + ( 4.1616724 + y ) * y;
	float v = a / b;
	float theta_sintheta = ( x > 0.0 ) ? v : 0.5 * inversesqrt( max( 1.0 - x * x, 1e-7 ) ) - v;
	return cross( v1, v2 ) * theta_sintheta;
}
vec3 LTC_Evaluate( const in vec3 N, const in vec3 V, const in vec3 P, const in mat3 mInv, const in vec3 rectCoords[ 4 ] ) {
	vec3 v1 = rectCoords[ 1 ] - rectCoords[ 0 ];
	vec3 v2 = rectCoords[ 3 ] - rectCoords[ 0 ];
	vec3 lightNormal = cross( v1, v2 );
	if( dot( lightNormal, P - rectCoords[ 0 ] ) < 0.0 ) return vec3( 0.0 );
	vec3 T1, T2;
	T1 = normalize( V - N * dot( V, N ) );
	T2 = - cross( N, T1 );
	mat3 mat = mInv * transpose( mat3( T1, T2, N ) );
	vec3 coords[ 4 ];
	coords[ 0 ] = mat * ( rectCoords[ 0 ] - P );
	coords[ 1 ] = mat * ( rectCoords[ 1 ] - P );
	coords[ 2 ] = mat * ( rectCoords[ 2 ] - P );
	coords[ 3 ] = mat * ( rectCoords[ 3 ] - P );
	coords[ 0 ] = normalize( coords[ 0 ] );
	coords[ 1 ] = normalize( coords[ 1 ] );
	coords[ 2 ] = normalize( coords[ 2 ] );
	coords[ 3 ] = normalize( coords[ 3 ] );
	vec3 vectorFormFactor = vec3( 0.0 );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 0 ], coords[ 1 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 1 ], coords[ 2 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 2 ], coords[ 3 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 3 ], coords[ 0 ] );
	float result = LTC_ClippedSphereFormFactor( vectorFormFactor );
	return vec3( result );
}
#if defined( USE_SHEEN )
float D_Charlie( float roughness, float dotNH ) {
	float alpha = pow2( roughness );
	float invAlpha = 1.0 / alpha;
	float cos2h = dotNH * dotNH;
	float sin2h = max( 1.0 - cos2h, 0.0078125 );
	return ( 2.0 + invAlpha ) * pow( sin2h, invAlpha * 0.5 ) / ( 2.0 * PI );
}
float V_Neubelt( float dotNV, float dotNL ) {
	return saturate( 1.0 / ( 4.0 * ( dotNL + dotNV - dotNL * dotNV ) ) );
}
vec3 BRDF_Sheen( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, vec3 sheenColor, const in float sheenRoughness ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float D = D_Charlie( sheenRoughness, dotNH );
	float V = V_Neubelt( dotNV, dotNL );
	return sheenColor * ( D * V );
}
#endif
float IBLSheenBRDF( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	float r2 = roughness * roughness;
	float rInv = 1.0 / ( roughness + 0.1 );
	float a = -1.9362 + 1.0678 * roughness + 0.4573 * r2 - 0.8469 * rInv;
	float b = -0.6014 + 0.5538 * roughness - 0.4670 * r2 - 0.1255 * rInv;
	float DG = exp( a * dotNV + b );
	return saturate( DG );
}
vec3 EnvironmentBRDF( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 fab = texture2D( dfgLUT, vec2( roughness, dotNV ) ).rg;
	return specularColor * fab.x + specularF90 * fab.y;
}
#ifdef USE_IRIDESCENCE
void computeMultiscatteringIridescence( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float iridescence, const in vec3 iridescenceF0, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#else
void computeMultiscattering( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#endif
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 fab = texture2D( dfgLUT, vec2( roughness, dotNV ) ).rg;
	#ifdef USE_IRIDESCENCE
		vec3 Fr = mix( specularColor, iridescenceF0, iridescence );
	#else
		vec3 Fr = specularColor;
	#endif
	vec3 FssEss = Fr * fab.x + specularF90 * fab.y;
	float Ess = fab.x + fab.y;
	float Ems = 1.0 - Ess;
	vec3 Favg = Fr + ( 1.0 - Fr ) * 0.047619;	vec3 Fms = FssEss * Favg / ( 1.0 - Ems * Favg );
	singleScatter += FssEss;
	multiScatter += Fms * Ems;
}
vec3 BRDF_GGX_Multiscatter( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 singleScatter = BRDF_GGX( lightDir, viewDir, normal, material );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 dfgV = texture2D( dfgLUT, vec2( material.roughness, dotNV ) ).rg;
	vec2 dfgL = texture2D( dfgLUT, vec2( material.roughness, dotNL ) ).rg;
	vec3 FssEss_V = material.specularColorBlended * dfgV.x + material.specularF90 * dfgV.y;
	vec3 FssEss_L = material.specularColorBlended * dfgL.x + material.specularF90 * dfgL.y;
	float Ess_V = dfgV.x + dfgV.y;
	float Ess_L = dfgL.x + dfgL.y;
	float Ems_V = 1.0 - Ess_V;
	float Ems_L = 1.0 - Ess_L;
	vec3 Favg = material.specularColorBlended + ( 1.0 - material.specularColorBlended ) * 0.047619;
	vec3 Fms = FssEss_V * FssEss_L * Favg / ( 1.0 - Ems_V * Ems_L * Favg + EPSILON );
	float compensationFactor = Ems_V * Ems_L;
	vec3 multiScatter = Fms * compensationFactor;
	return singleScatter + multiScatter;
}
#if NUM_RECT_AREA_LIGHTS > 0
	void RE_Direct_RectArea_Physical( const in RectAreaLight rectAreaLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
		vec3 normal = geometryNormal;
		vec3 viewDir = geometryViewDir;
		vec3 position = geometryPosition;
		vec3 lightPos = rectAreaLight.position;
		vec3 halfWidth = rectAreaLight.halfWidth;
		vec3 halfHeight = rectAreaLight.halfHeight;
		vec3 lightColor = rectAreaLight.color;
		float roughness = material.roughness;
		vec3 rectCoords[ 4 ];
		rectCoords[ 0 ] = lightPos + halfWidth - halfHeight;		rectCoords[ 1 ] = lightPos - halfWidth - halfHeight;
		rectCoords[ 2 ] = lightPos - halfWidth + halfHeight;
		rectCoords[ 3 ] = lightPos + halfWidth + halfHeight;
		vec2 uv = LTC_Uv( normal, viewDir, roughness );
		vec4 t1 = texture2D( ltc_1, uv );
		vec4 t2 = texture2D( ltc_2, uv );
		mat3 mInv = mat3(
			vec3( t1.x, 0, t1.y ),
			vec3(    0, 1,    0 ),
			vec3( t1.z, 0, t1.w )
		);
		vec3 fresnel = ( material.specularColorBlended * t2.x + ( material.specularF90 - material.specularColorBlended ) * t2.y );
		reflectedLight.directSpecular += lightColor * fresnel * LTC_Evaluate( normal, viewDir, position, mInv, rectCoords );
		reflectedLight.directDiffuse += lightColor * material.diffuseContribution * LTC_Evaluate( normal, viewDir, position, mat3( 1.0 ), rectCoords );
		#ifdef USE_CLEARCOAT
			vec3 Ncc = geometryClearcoatNormal;
			vec2 uvClearcoat = LTC_Uv( Ncc, viewDir, material.clearcoatRoughness );
			vec4 t1Clearcoat = texture2D( ltc_1, uvClearcoat );
			vec4 t2Clearcoat = texture2D( ltc_2, uvClearcoat );
			mat3 mInvClearcoat = mat3(
				vec3( t1Clearcoat.x, 0, t1Clearcoat.y ),
				vec3(             0, 1,             0 ),
				vec3( t1Clearcoat.z, 0, t1Clearcoat.w )
			);
			vec3 fresnelClearcoat = material.clearcoatF0 * t2Clearcoat.x + ( material.clearcoatF90 - material.clearcoatF0 ) * t2Clearcoat.y;
			clearcoatSpecularDirect += lightColor * fresnelClearcoat * LTC_Evaluate( Ncc, viewDir, position, mInvClearcoat, rectCoords );
		#endif
	}
#endif
void RE_Direct_Physical( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	#ifdef USE_CLEARCOAT
		float dotNLcc = saturate( dot( geometryClearcoatNormal, directLight.direction ) );
		vec3 ccIrradiance = dotNLcc * directLight.color;
		clearcoatSpecularDirect += ccIrradiance * BRDF_GGX_Clearcoat( directLight.direction, geometryViewDir, geometryClearcoatNormal, material );
	#endif
	#ifdef USE_SHEEN
 
 		sheenSpecularDirect += irradiance * BRDF_Sheen( directLight.direction, geometryViewDir, geometryNormal, material.sheenColor, material.sheenRoughness );
 
 		float sheenAlbedoV = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
 		float sheenAlbedoL = IBLSheenBRDF( geometryNormal, directLight.direction, material.sheenRoughness );
 
 		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * max( sheenAlbedoV, sheenAlbedoL );
 
 		irradiance *= sheenEnergyComp;
 
 	#endif
	reflectedLight.directSpecular += irradiance * BRDF_GGX_Multiscatter( directLight.direction, geometryViewDir, geometryNormal, material );
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseContribution );
}
void RE_IndirectDiffuse_Physical( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 diffuse = irradiance * BRDF_Lambert( material.diffuseContribution );
	#ifdef USE_SHEEN
		float sheenAlbedo = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * sheenAlbedo;
		diffuse *= sheenEnergyComp;
	#endif
	reflectedLight.indirectDiffuse += diffuse;
}
void RE_IndirectSpecular_Physical( const in vec3 radiance, const in vec3 irradiance, const in vec3 clearcoatRadiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight) {
	#ifdef USE_CLEARCOAT
		clearcoatSpecularIndirect += clearcoatRadiance * EnvironmentBRDF( geometryClearcoatNormal, geometryViewDir, material.clearcoatF0, material.clearcoatF90, material.clearcoatRoughness );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularIndirect += irradiance * material.sheenColor * IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness ) * RECIPROCAL_PI;
 	#endif
	vec3 singleScatteringDielectric = vec3( 0.0 );
	vec3 multiScatteringDielectric = vec3( 0.0 );
	vec3 singleScatteringMetallic = vec3( 0.0 );
	vec3 multiScatteringMetallic = vec3( 0.0 );
	#ifdef USE_IRIDESCENCE
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.iridescence, material.iridescenceFresnelDielectric, material.roughness, singleScatteringDielectric, multiScatteringDielectric );
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.diffuseColor, material.specularF90, material.iridescence, material.iridescenceFresnelMetallic, material.roughness, singleScatteringMetallic, multiScatteringMetallic );
	#else
		computeMultiscattering( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.roughness, singleScatteringDielectric, multiScatteringDielectric );
		computeMultiscattering( geometryNormal, geometryViewDir, material.diffuseColor, material.specularF90, material.roughness, singleScatteringMetallic, multiScatteringMetallic );
	#endif
	vec3 singleScattering = mix( singleScatteringDielectric, singleScatteringMetallic, material.metalness );
	vec3 multiScattering = mix( multiScatteringDielectric, multiScatteringMetallic, material.metalness );
	vec3 totalScatteringDielectric = singleScatteringDielectric + multiScatteringDielectric;
	vec3 diffuse = material.diffuseContribution * ( 1.0 - totalScatteringDielectric );
	vec3 cosineWeightedIrradiance = irradiance * RECIPROCAL_PI;
	vec3 indirectSpecular = radiance * singleScattering;
	indirectSpecular += multiScattering * cosineWeightedIrradiance;
	vec3 indirectDiffuse = diffuse * cosineWeightedIrradiance;
	#ifdef USE_SHEEN
		float sheenAlbedo = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * sheenAlbedo;
		indirectSpecular *= sheenEnergyComp;
		indirectDiffuse *= sheenEnergyComp;
	#endif
	reflectedLight.indirectSpecular += indirectSpecular;
	reflectedLight.indirectDiffuse += indirectDiffuse;
}
#define RE_Direct				RE_Direct_Physical
#define RE_Direct_RectArea		RE_Direct_RectArea_Physical
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Physical
#define RE_IndirectSpecular		RE_IndirectSpecular_Physical
float computeSpecularOcclusion( const in float dotNV, const in float ambientOcclusion, const in float roughness ) {
	return saturate( pow( dotNV + ambientOcclusion, exp2( - 16.0 * roughness - 1.0 ) ) - 1.0 + ambientOcclusion );
}`,yg=`
vec3 geometryPosition = - vViewPosition;
vec3 geometryNormal = normal;
vec3 geometryViewDir = ( isOrthographic ) ? vec3( 0, 0, 1 ) : normalize( vViewPosition );
vec3 geometryClearcoatNormal = vec3( 0.0 );
#ifdef USE_CLEARCOAT
	geometryClearcoatNormal = clearcoatNormal;
#endif
#ifdef USE_IRIDESCENCE
	float dotNVi = saturate( dot( normal, geometryViewDir ) );
	if ( material.iridescenceThickness == 0.0 ) {
		material.iridescence = 0.0;
	} else {
		material.iridescence = saturate( material.iridescence );
	}
	if ( material.iridescence > 0.0 ) {
		material.iridescenceFresnelDielectric = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.specularColor );
		material.iridescenceFresnelMetallic = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.diffuseColor );
		material.iridescenceFresnel = mix( material.iridescenceFresnelDielectric, material.iridescenceFresnelMetallic, material.metalness );
		material.iridescenceF0 = Schlick_to_F0( material.iridescenceFresnel, 1.0, dotNVi );
	}
#endif
IncidentLight directLight;
#if ( NUM_POINT_LIGHTS > 0 ) && defined( RE_Direct )
	PointLight pointLight;
	#if defined( USE_SHADOWMAP ) && NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHTS; i ++ ) {
		pointLight = pointLights[ i ];
		getPointLightInfo( pointLight, geometryPosition, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_POINT_LIGHT_SHADOWS ) && ( defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_BASIC ) )
		pointLightShadow = pointLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getPointShadow( pointShadowMap[ i ], pointLightShadow.shadowMapSize, pointLightShadow.shadowIntensity, pointLightShadow.shadowBias, pointLightShadow.shadowRadius, vPointShadowCoord[ i ], pointLightShadow.shadowCameraNear, pointLightShadow.shadowCameraFar ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_SPOT_LIGHTS > 0 ) && defined( RE_Direct )
	SpotLight spotLight;
	vec4 spotColor;
	vec3 spotLightCoord;
	bool inSpotLightMap;
	#if defined( USE_SHADOWMAP ) && NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHTS; i ++ ) {
		spotLight = spotLights[ i ];
		getSpotLightInfo( spotLight, geometryPosition, directLight );
		#if ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#define SPOT_LIGHT_MAP_INDEX UNROLLED_LOOP_INDEX
		#elif ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		#define SPOT_LIGHT_MAP_INDEX NUM_SPOT_LIGHT_MAPS
		#else
		#define SPOT_LIGHT_MAP_INDEX ( UNROLLED_LOOP_INDEX - NUM_SPOT_LIGHT_SHADOWS + NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#endif
		#if ( SPOT_LIGHT_MAP_INDEX < NUM_SPOT_LIGHT_MAPS )
			spotLightCoord = vSpotLightCoord[ i ].xyz / vSpotLightCoord[ i ].w;
			inSpotLightMap = all( lessThan( abs( spotLightCoord * 2. - 1. ), vec3( 1.0 ) ) );
			spotColor = texture2D( spotLightMap[ SPOT_LIGHT_MAP_INDEX ], spotLightCoord.xy );
			directLight.color = inSpotLightMap ? directLight.color * spotColor.rgb : directLight.color;
		#endif
		#undef SPOT_LIGHT_MAP_INDEX
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		spotLightShadow = spotLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( spotShadowMap[ i ], spotLightShadow.shadowMapSize, spotLightShadow.shadowIntensity, spotLightShadow.shadowBias, spotLightShadow.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_DIR_LIGHTS > 0 ) && defined( RE_Direct )
	DirectionalLight directionalLight;
	#if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHTS; i ++ ) {
		directionalLight = directionalLights[ i ];
		getDirectionalLightInfo( directionalLight, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_DIR_LIGHT_SHADOWS )
		directionalLightShadow = directionalLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowIntensity, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_RECT_AREA_LIGHTS > 0 ) && defined( RE_Direct_RectArea )
	RectAreaLight rectAreaLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_RECT_AREA_LIGHTS; i ++ ) {
		rectAreaLight = rectAreaLights[ i ];
		RE_Direct_RectArea( rectAreaLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if defined( RE_IndirectDiffuse )
	vec3 iblIrradiance = vec3( 0.0 );
	vec3 irradiance = getAmbientLightIrradiance( ambientLightColor );
	#if defined( USE_LIGHT_PROBES )
		irradiance += getLightProbeIrradiance( lightProbe, geometryNormal );
	#endif
	#if ( NUM_HEMI_LIGHTS > 0 )
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_HEMI_LIGHTS; i ++ ) {
			irradiance += getHemisphereLightIrradiance( hemisphereLights[ i ], geometryNormal );
		}
		#pragma unroll_loop_end
	#endif
#endif
#if defined( RE_IndirectSpecular )
	vec3 radiance = vec3( 0.0 );
	vec3 clearcoatRadiance = vec3( 0.0 );
#endif`,Eg=`#if defined( RE_IndirectDiffuse )
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;
		irradiance += lightMapIrradiance;
	#endif
	#if defined( USE_ENVMAP ) && defined( ENVMAP_TYPE_CUBE_UV )
		#if defined( STANDARD ) || defined( LAMBERT ) || defined( PHONG )
			iblIrradiance += getIBLIrradiance( geometryNormal );
		#endif
	#endif
#endif
#if defined( USE_ENVMAP ) && defined( RE_IndirectSpecular )
	#ifdef USE_ANISOTROPY
		radiance += getIBLAnisotropyRadiance( geometryViewDir, geometryNormal, material.roughness, material.anisotropyB, material.anisotropy );
	#else
		radiance += getIBLRadiance( geometryViewDir, geometryNormal, material.roughness );
	#endif
	#ifdef USE_CLEARCOAT
		clearcoatRadiance += getIBLRadiance( geometryViewDir, geometryClearcoatNormal, material.clearcoatRoughness );
	#endif
#endif`,Tg=`#if defined( RE_IndirectDiffuse )
	#if defined( LAMBERT ) || defined( PHONG )
		irradiance += iblIrradiance;
	#endif
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,bg=`#if defined( USE_LOGARITHMIC_DEPTH_BUFFER )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,Ag=`#if defined( USE_LOGARITHMIC_DEPTH_BUFFER )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,wg=`#ifdef USE_LOGARITHMIC_DEPTH_BUFFER
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,Rg=`#ifdef USE_LOGARITHMIC_DEPTH_BUFFER
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,Cg=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,Pg=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,Dg=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
	#if defined( USE_POINTS_UV )
		vec2 uv = vUv;
	#else
		vec2 uv = ( uvTransform * vec3( gl_PointCoord.x, 1.0 - gl_PointCoord.y, 1 ) ).xy;
	#endif
#endif
#ifdef USE_MAP
	diffuseColor *= texture2D( map, uv );
#endif
#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, uv ).g;
#endif`,Lg=`#if defined( USE_POINTS_UV )
	varying vec2 vUv;
#else
	#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
		uniform mat3 uvTransform;
	#endif
#endif
#ifdef USE_MAP
	uniform sampler2D map;
#endif
#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,Ig=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,Ug=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,Ng=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,Fg=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,Og=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,Bg=`#ifdef USE_MORPHTARGETS
	#ifndef USE_INSTANCING_MORPH
		uniform float morphTargetBaseInfluence;
		uniform float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	#endif
	uniform sampler2DArray morphTargetsTexture;
	uniform ivec2 morphTargetsTextureSize;
	vec4 getMorph( const in int vertexIndex, const in int morphTargetIndex, const in int offset ) {
		int texelIndex = vertexIndex * MORPHTARGETS_TEXTURE_STRIDE + offset;
		int y = texelIndex / morphTargetsTextureSize.x;
		int x = texelIndex - y * morphTargetsTextureSize.x;
		ivec3 morphUV = ivec3( x, y, morphTargetIndex );
		return texelFetch( morphTargetsTexture, morphUV, 0 );
	}
#endif`,kg=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,zg=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
#ifdef FLAT_SHADED
	vec3 fdx = dFdx( vViewPosition );
	vec3 fdy = dFdy( vViewPosition );
	vec3 normal = normalize( cross( fdx, fdy ) );
#else
	vec3 normal = normalize( vNormal );
	#ifdef DOUBLE_SIDED
		normal *= faceDirection;
	#endif
#endif
#if defined( USE_NORMALMAP_TANGENTSPACE ) || defined( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY )
	#ifdef USE_TANGENT
		mat3 tbn = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn = getTangentFrame( - vViewPosition, normal,
		#if defined( USE_NORMALMAP )
			vNormalMapUv
		#elif defined( USE_CLEARCOAT_NORMALMAP )
			vClearcoatNormalMapUv
		#else
			vUv
		#endif
		);
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn[0] *= faceDirection;
		tbn[1] *= faceDirection;
	#endif
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	#ifdef USE_TANGENT
		mat3 tbn2 = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn2 = getTangentFrame( - vViewPosition, normal, vClearcoatNormalMapUv );
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn2[0] *= faceDirection;
		tbn2[1] *= faceDirection;
	#endif
#endif
vec3 nonPerturbedNormal = normal;`,Vg=`#ifdef USE_NORMALMAP_OBJECTSPACE
	normal = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#ifdef FLIP_SIDED
		normal = - normal;
	#endif
	#ifdef DOUBLE_SIDED
		normal = normal * faceDirection;
	#endif
	normal = normalize( normalMatrix * normal );
#elif defined( USE_NORMALMAP_TANGENTSPACE )
	vec3 mapN = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	mapN.xy *= normalScale;
	normal = normalize( tbn * mapN );
#elif defined( USE_BUMPMAP )
	normal = perturbNormalArb( - vViewPosition, normal, dHdxy_fwd(), faceDirection );
#endif`,Gg=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,Hg=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,Wg=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,Xg=`#ifdef USE_NORMALMAP
	uniform sampler2D normalMap;
	uniform vec2 normalScale;
#endif
#ifdef USE_NORMALMAP_OBJECTSPACE
	uniform mat3 normalMatrix;
#endif
#if ! defined ( USE_TANGENT ) && ( defined ( USE_NORMALMAP_TANGENTSPACE ) || defined ( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY ) )
	mat3 getTangentFrame( vec3 eye_pos, vec3 surf_norm, vec2 uv ) {
		vec3 q0 = dFdx( eye_pos.xyz );
		vec3 q1 = dFdy( eye_pos.xyz );
		vec2 st0 = dFdx( uv.st );
		vec2 st1 = dFdy( uv.st );
		vec3 N = surf_norm;
		vec3 q1perp = cross( q1, N );
		vec3 q0perp = cross( N, q0 );
		vec3 T = q1perp * st0.x + q0perp * st1.x;
		vec3 B = q1perp * st0.y + q0perp * st1.y;
		float det = max( dot( T, T ), dot( B, B ) );
		float scale = ( det == 0.0 ) ? 0.0 : inversesqrt( det );
		return mat3( T * scale, B * scale, N );
	}
#endif`,qg=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,Yg=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,$g=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,Kg=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,Zg=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,Jg=`vec3 packNormalToRGB( const in vec3 normal ) {
	return normalize( normal ) * 0.5 + 0.5;
}
vec3 unpackRGBToNormal( const in vec3 rgb ) {
	return 2.0 * rgb.xyz - 1.0;
}
const float PackUpscale = 256. / 255.;const float UnpackDownscale = 255. / 256.;const float ShiftRight8 = 1. / 256.;
const float Inv255 = 1. / 255.;
const vec4 PackFactors = vec4( 1.0, 256.0, 256.0 * 256.0, 256.0 * 256.0 * 256.0 );
const vec2 UnpackFactors2 = vec2( UnpackDownscale, 1.0 / PackFactors.g );
const vec3 UnpackFactors3 = vec3( UnpackDownscale / PackFactors.rg, 1.0 / PackFactors.b );
const vec4 UnpackFactors4 = vec4( UnpackDownscale / PackFactors.rgb, 1.0 / PackFactors.a );
vec4 packDepthToRGBA( const in float v ) {
	if( v <= 0.0 )
		return vec4( 0., 0., 0., 0. );
	if( v >= 1.0 )
		return vec4( 1., 1., 1., 1. );
	float vuf;
	float af = modf( v * PackFactors.a, vuf );
	float bf = modf( vuf * ShiftRight8, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec4( vuf * Inv255, gf * PackUpscale, bf * PackUpscale, af );
}
vec3 packDepthToRGB( const in float v ) {
	if( v <= 0.0 )
		return vec3( 0., 0., 0. );
	if( v >= 1.0 )
		return vec3( 1., 1., 1. );
	float vuf;
	float bf = modf( v * PackFactors.b, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec3( vuf * Inv255, gf * PackUpscale, bf );
}
vec2 packDepthToRG( const in float v ) {
	if( v <= 0.0 )
		return vec2( 0., 0. );
	if( v >= 1.0 )
		return vec2( 1., 1. );
	float vuf;
	float gf = modf( v * 256., vuf );
	return vec2( vuf * Inv255, gf );
}
float unpackRGBAToDepth( const in vec4 v ) {
	return dot( v, UnpackFactors4 );
}
float unpackRGBToDepth( const in vec3 v ) {
	return dot( v, UnpackFactors3 );
}
float unpackRGToDepth( const in vec2 v ) {
	return v.r * UnpackFactors2.r + v.g * UnpackFactors2.g;
}
vec4 pack2HalfToRGBA( const in vec2 v ) {
	vec4 r = vec4( v.x, fract( v.x * 255.0 ), v.y, fract( v.y * 255.0 ) );
	return vec4( r.x - r.y / 255.0, r.y, r.z - r.w / 255.0, r.w );
}
vec2 unpackRGBATo2Half( const in vec4 v ) {
	return vec2( v.x + ( v.y / 255.0 ), v.z + ( v.w / 255.0 ) );
}
float viewZToOrthographicDepth( const in float viewZ, const in float near, const in float far ) {
	return ( viewZ + near ) / ( near - far );
}
float orthographicDepthToViewZ( const in float depth, const in float near, const in float far ) {
	#ifdef USE_REVERSED_DEPTH_BUFFER
	
		return depth * ( far - near ) - far;
	#else
		return depth * ( near - far ) - near;
	#endif
}
float viewZToPerspectiveDepth( const in float viewZ, const in float near, const in float far ) {
	return ( ( near + viewZ ) * far ) / ( ( far - near ) * viewZ );
}
float perspectiveDepthToViewZ( const in float depth, const in float near, const in float far ) {
	
	#ifdef USE_REVERSED_DEPTH_BUFFER
		return ( near * far ) / ( ( near - far ) * depth - near );
	#else
		return ( near * far ) / ( ( far - near ) * depth - far );
	#endif
}`,jg=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,Qg=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,t0=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,e0=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,n0=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,i0=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,r0=`#if NUM_SPOT_LIGHT_COORDS > 0
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#if NUM_SPOT_LIGHT_MAPS > 0
	uniform sampler2D spotLightMap[ NUM_SPOT_LIGHT_MAPS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform sampler2DShadow directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		#else
			uniform sampler2D directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		#endif
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform sampler2DShadow spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		#else
			uniform sampler2D spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		#endif
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform samplerCubeShadow pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		#elif defined( SHADOWMAP_TYPE_BASIC )
			uniform samplerCube pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		#endif
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
	#if defined( SHADOWMAP_TYPE_PCF )
		float interleavedGradientNoise( vec2 position ) {
			return fract( 52.9829189 * fract( dot( position, vec2( 0.06711056, 0.00583715 ) ) ) );
		}
		vec2 vogelDiskSample( int sampleIndex, int samplesCount, float phi ) {
			const float goldenAngle = 2.399963229728653;
			float r = sqrt( ( float( sampleIndex ) + 0.5 ) / float( samplesCount ) );
			float theta = float( sampleIndex ) * goldenAngle + phi;
			return vec2( cos( theta ), sin( theta ) ) * r;
		}
	#endif
	#if defined( SHADOWMAP_TYPE_PCF )
		float getShadow( sampler2DShadow shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			shadowCoord.z += shadowBias;
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
				float radius = shadowRadius * texelSize.x;
				float phi = interleavedGradientNoise( gl_FragCoord.xy ) * PI2;
				shadow = (
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 0, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 1, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 2, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 3, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 4, 5, phi ) * radius, shadowCoord.z ) )
				) * 0.2;
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#elif defined( SHADOWMAP_TYPE_VSM )
		float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				shadowCoord.z -= shadowBias;
			#else
				shadowCoord.z += shadowBias;
			#endif
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				vec2 distribution = texture2D( shadowMap, shadowCoord.xy ).rg;
				float mean = distribution.x;
				float variance = distribution.y * distribution.y;
				#ifdef USE_REVERSED_DEPTH_BUFFER
					float hard_shadow = step( mean, shadowCoord.z );
				#else
					float hard_shadow = step( shadowCoord.z, mean );
				#endif
				
				if ( hard_shadow == 1.0 ) {
					shadow = 1.0;
				} else {
					variance = max( variance, 0.0000001 );
					float d = shadowCoord.z - mean;
					float p_max = variance / ( variance + d * d );
					p_max = clamp( ( p_max - 0.3 ) / 0.65, 0.0, 1.0 );
					shadow = max( hard_shadow, p_max );
				}
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#else
		float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				shadowCoord.z -= shadowBias;
			#else
				shadowCoord.z += shadowBias;
			#endif
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				float depth = texture2D( shadowMap, shadowCoord.xy ).r;
				#ifdef USE_REVERSED_DEPTH_BUFFER
					shadow = step( depth, shadowCoord.z );
				#else
					shadow = step( shadowCoord.z, depth );
				#endif
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
	#if defined( SHADOWMAP_TYPE_PCF )
	float getPointShadow( samplerCubeShadow shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		vec3 bd3D = normalize( lightToPosition );
		vec3 absVec = abs( lightToPosition );
		float viewSpaceZ = max( max( absVec.x, absVec.y ), absVec.z );
		if ( viewSpaceZ - shadowCameraFar <= 0.0 && viewSpaceZ - shadowCameraNear >= 0.0 ) {
			#ifdef USE_REVERSED_DEPTH_BUFFER
				float dp = ( shadowCameraNear * ( shadowCameraFar - viewSpaceZ ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
				dp -= shadowBias;
			#else
				float dp = ( shadowCameraFar * ( viewSpaceZ - shadowCameraNear ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
				dp += shadowBias;
			#endif
			float texelSize = shadowRadius / shadowMapSize.x;
			vec3 absDir = abs( bd3D );
			vec3 tangent = absDir.x > absDir.z ? vec3( 0.0, 1.0, 0.0 ) : vec3( 1.0, 0.0, 0.0 );
			tangent = normalize( cross( bd3D, tangent ) );
			vec3 bitangent = cross( bd3D, tangent );
			float phi = interleavedGradientNoise( gl_FragCoord.xy ) * PI2;
			vec2 sample0 = vogelDiskSample( 0, 5, phi );
			vec2 sample1 = vogelDiskSample( 1, 5, phi );
			vec2 sample2 = vogelDiskSample( 2, 5, phi );
			vec2 sample3 = vogelDiskSample( 3, 5, phi );
			vec2 sample4 = vogelDiskSample( 4, 5, phi );
			shadow = (
				texture( shadowMap, vec4( bd3D + ( tangent * sample0.x + bitangent * sample0.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample1.x + bitangent * sample1.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample2.x + bitangent * sample2.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample3.x + bitangent * sample3.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample4.x + bitangent * sample4.y ) * texelSize, dp ) )
			) * 0.2;
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	#elif defined( SHADOWMAP_TYPE_BASIC )
	float getPointShadow( samplerCube shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		vec3 absVec = abs( lightToPosition );
		float viewSpaceZ = max( max( absVec.x, absVec.y ), absVec.z );
		if ( viewSpaceZ - shadowCameraFar <= 0.0 && viewSpaceZ - shadowCameraNear >= 0.0 ) {
			float dp = ( shadowCameraFar * ( viewSpaceZ - shadowCameraNear ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
			dp += shadowBias;
			vec3 bd3D = normalize( lightToPosition );
			float depth = textureCube( shadowMap, bd3D ).r;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				depth = 1.0 - depth;
			#endif
			shadow = step( dp, depth );
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	#endif
	#endif
#endif`,s0=`#if NUM_SPOT_LIGHT_COORDS > 0
	uniform mat4 spotLightMatrix[ NUM_SPOT_LIGHT_COORDS ];
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform mat4 directionalShadowMatrix[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform mat4 pointShadowMatrix[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
#endif`,a0=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
	vec3 shadowWorldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
	vec4 shadowWorldPosition;
#endif
#if defined( USE_SHADOWMAP )
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * directionalLightShadows[ i ].shadowNormalBias, 0 );
			vDirectionalShadowCoord[ i ] = directionalShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * pointLightShadows[ i ].shadowNormalBias, 0 );
			vPointShadowCoord[ i ] = pointShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
#endif
#if NUM_SPOT_LIGHT_COORDS > 0
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_COORDS; i ++ ) {
		shadowWorldPosition = worldPosition;
		#if ( defined( USE_SHADOWMAP ) && UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
			shadowWorldPosition.xyz += shadowWorldNormal * spotLightShadows[ i ].shadowNormalBias;
		#endif
		vSpotLightCoord[ i ] = spotLightMatrix[ i ] * shadowWorldPosition;
	}
	#pragma unroll_loop_end
#endif`,o0=`float getShadowMask() {
	float shadow = 1.0;
	#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
		directionalLight = directionalLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( directionalShadowMap[ i ], directionalLight.shadowMapSize, directionalLight.shadowIntensity, directionalLight.shadowBias, directionalLight.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_SHADOWS; i ++ ) {
		spotLight = spotLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( spotShadowMap[ i ], spotLight.shadowMapSize, spotLight.shadowIntensity, spotLight.shadowBias, spotLight.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0 && ( defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_BASIC ) )
	PointLightShadow pointLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
		pointLight = pointLightShadows[ i ];
		shadow *= receiveShadow ? getPointShadow( pointShadowMap[ i ], pointLight.shadowMapSize, pointLight.shadowIntensity, pointLight.shadowBias, pointLight.shadowRadius, vPointShadowCoord[ i ], pointLight.shadowCameraNear, pointLight.shadowCameraFar ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#endif
	return shadow;
}`,l0=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,c0=`#ifdef USE_SKINNING
	uniform mat4 bindMatrix;
	uniform mat4 bindMatrixInverse;
	uniform highp sampler2D boneTexture;
	mat4 getBoneMatrix( const in float i ) {
		int size = textureSize( boneTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( boneTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( boneTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( boneTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( boneTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
#endif`,u0=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,f0=`#ifdef USE_SKINNING
	mat4 skinMatrix = mat4( 0.0 );
	skinMatrix += skinWeight.x * boneMatX;
	skinMatrix += skinWeight.y * boneMatY;
	skinMatrix += skinWeight.z * boneMatZ;
	skinMatrix += skinWeight.w * boneMatW;
	skinMatrix = bindMatrixInverse * skinMatrix * bindMatrix;
	objectNormal = vec4( skinMatrix * vec4( objectNormal, 0.0 ) ).xyz;
	#ifdef USE_TANGENT
		objectTangent = vec4( skinMatrix * vec4( objectTangent, 0.0 ) ).xyz;
	#endif
#endif`,h0=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,d0=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,p0=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,m0=`#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
uniform float toneMappingExposure;
vec3 LinearToneMapping( vec3 color ) {
	return saturate( toneMappingExposure * color );
}
vec3 ReinhardToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	return saturate( color / ( vec3( 1.0 ) + color ) );
}
vec3 CineonToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	color = max( vec3( 0.0 ), color - 0.004 );
	return pow( ( color * ( 6.2 * color + 0.5 ) ) / ( color * ( 6.2 * color + 1.7 ) + 0.06 ), vec3( 2.2 ) );
}
vec3 RRTAndODTFit( vec3 v ) {
	vec3 a = v * ( v + 0.0245786 ) - 0.000090537;
	vec3 b = v * ( 0.983729 * v + 0.4329510 ) + 0.238081;
	return a / b;
}
vec3 ACESFilmicToneMapping( vec3 color ) {
	const mat3 ACESInputMat = mat3(
		vec3( 0.59719, 0.07600, 0.02840 ),		vec3( 0.35458, 0.90834, 0.13383 ),
		vec3( 0.04823, 0.01566, 0.83777 )
	);
	const mat3 ACESOutputMat = mat3(
		vec3(  1.60475, -0.10208, -0.00327 ),		vec3( -0.53108,  1.10813, -0.07276 ),
		vec3( -0.07367, -0.00605,  1.07602 )
	);
	color *= toneMappingExposure / 0.6;
	color = ACESInputMat * color;
	color = RRTAndODTFit( color );
	color = ACESOutputMat * color;
	return saturate( color );
}
const mat3 LINEAR_REC2020_TO_LINEAR_SRGB = mat3(
	vec3( 1.6605, - 0.1246, - 0.0182 ),
	vec3( - 0.5876, 1.1329, - 0.1006 ),
	vec3( - 0.0728, - 0.0083, 1.1187 )
);
const mat3 LINEAR_SRGB_TO_LINEAR_REC2020 = mat3(
	vec3( 0.6274, 0.0691, 0.0164 ),
	vec3( 0.3293, 0.9195, 0.0880 ),
	vec3( 0.0433, 0.0113, 0.8956 )
);
vec3 agxDefaultContrastApprox( vec3 x ) {
	vec3 x2 = x * x;
	vec3 x4 = x2 * x2;
	return + 15.5 * x4 * x2
		- 40.14 * x4 * x
		+ 31.96 * x4
		- 6.868 * x2 * x
		+ 0.4298 * x2
		+ 0.1191 * x
		- 0.00232;
}
vec3 AgXToneMapping( vec3 color ) {
	const mat3 AgXInsetMatrix = mat3(
		vec3( 0.856627153315983, 0.137318972929847, 0.11189821299995 ),
		vec3( 0.0951212405381588, 0.761241990602591, 0.0767994186031903 ),
		vec3( 0.0482516061458583, 0.101439036467562, 0.811302368396859 )
	);
	const mat3 AgXOutsetMatrix = mat3(
		vec3( 1.1271005818144368, - 0.1413297634984383, - 0.14132976349843826 ),
		vec3( - 0.11060664309660323, 1.157823702216272, - 0.11060664309660294 ),
		vec3( - 0.016493938717834573, - 0.016493938717834257, 1.2519364065950405 )
	);
	const float AgxMinEv = - 12.47393;	const float AgxMaxEv = 4.026069;
	color *= toneMappingExposure;
	color = LINEAR_SRGB_TO_LINEAR_REC2020 * color;
	color = AgXInsetMatrix * color;
	color = max( color, 1e-10 );	color = log2( color );
	color = ( color - AgxMinEv ) / ( AgxMaxEv - AgxMinEv );
	color = clamp( color, 0.0, 1.0 );
	color = agxDefaultContrastApprox( color );
	color = AgXOutsetMatrix * color;
	color = pow( max( vec3( 0.0 ), color ), vec3( 2.2 ) );
	color = LINEAR_REC2020_TO_LINEAR_SRGB * color;
	color = clamp( color, 0.0, 1.0 );
	return color;
}
vec3 NeutralToneMapping( vec3 color ) {
	const float StartCompression = 0.8 - 0.04;
	const float Desaturation = 0.15;
	color *= toneMappingExposure;
	float x = min( color.r, min( color.g, color.b ) );
	float offset = x < 0.08 ? x - 6.25 * x * x : 0.04;
	color -= offset;
	float peak = max( color.r, max( color.g, color.b ) );
	if ( peak < StartCompression ) return color;
	float d = 1. - StartCompression;
	float newPeak = 1. - d * d / ( peak + d - StartCompression );
	color *= newPeak / peak;
	float g = 1. - 1. / ( Desaturation * ( peak - newPeak ) + 1. );
	return mix( color, vec3( newPeak ), g );
}
vec3 CustomToneMapping( vec3 color ) { return color; }`,_0=`#ifdef USE_TRANSMISSION
	material.transmission = transmission;
	material.transmissionAlpha = 1.0;
	material.thickness = thickness;
	material.attenuationDistance = attenuationDistance;
	material.attenuationColor = attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		material.transmission *= texture2D( transmissionMap, vTransmissionMapUv ).r;
	#endif
	#ifdef USE_THICKNESSMAP
		material.thickness *= texture2D( thicknessMap, vThicknessMapUv ).g;
	#endif
	vec3 pos = vWorldPosition;
	vec3 v = normalize( cameraPosition - pos );
	vec3 n = inverseTransformDirection( normal, viewMatrix );
	vec4 transmitted = getIBLVolumeRefraction(
		n, v, material.roughness, material.diffuseContribution, material.specularColorBlended, material.specularF90,
		pos, modelMatrix, viewMatrix, projectionMatrix, material.dispersion, material.ior, material.thickness,
		material.attenuationColor, material.attenuationDistance );
	material.transmissionAlpha = mix( material.transmissionAlpha, transmitted.a, material.transmission );
	totalDiffuse = mix( totalDiffuse, transmitted.rgb, material.transmission );
#endif`,g0=`#ifdef USE_TRANSMISSION
	uniform float transmission;
	uniform float thickness;
	uniform float attenuationDistance;
	uniform vec3 attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		uniform sampler2D transmissionMap;
	#endif
	#ifdef USE_THICKNESSMAP
		uniform sampler2D thicknessMap;
	#endif
	uniform vec2 transmissionSamplerSize;
	uniform sampler2D transmissionSamplerMap;
	uniform mat4 modelMatrix;
	uniform mat4 projectionMatrix;
	varying vec3 vWorldPosition;
	float w0( float a ) {
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - a + 3.0 ) - 3.0 ) + 1.0 );
	}
	float w1( float a ) {
		return ( 1.0 / 6.0 ) * ( a *  a * ( 3.0 * a - 6.0 ) + 4.0 );
	}
	float w2( float a ){
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - 3.0 * a + 3.0 ) + 3.0 ) + 1.0 );
	}
	float w3( float a ) {
		return ( 1.0 / 6.0 ) * ( a * a * a );
	}
	float g0( float a ) {
		return w0( a ) + w1( a );
	}
	float g1( float a ) {
		return w2( a ) + w3( a );
	}
	float h0( float a ) {
		return - 1.0 + w1( a ) / ( w0( a ) + w1( a ) );
	}
	float h1( float a ) {
		return 1.0 + w3( a ) / ( w2( a ) + w3( a ) );
	}
	vec4 bicubic( sampler2D tex, vec2 uv, vec4 texelSize, float lod ) {
		uv = uv * texelSize.zw + 0.5;
		vec2 iuv = floor( uv );
		vec2 fuv = fract( uv );
		float g0x = g0( fuv.x );
		float g1x = g1( fuv.x );
		float h0x = h0( fuv.x );
		float h1x = h1( fuv.x );
		float h0y = h0( fuv.y );
		float h1y = h1( fuv.y );
		vec2 p0 = ( vec2( iuv.x + h0x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p1 = ( vec2( iuv.x + h1x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p2 = ( vec2( iuv.x + h0x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		vec2 p3 = ( vec2( iuv.x + h1x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		return g0( fuv.y ) * ( g0x * textureLod( tex, p0, lod ) + g1x * textureLod( tex, p1, lod ) ) +
			g1( fuv.y ) * ( g0x * textureLod( tex, p2, lod ) + g1x * textureLod( tex, p3, lod ) );
	}
	vec4 textureBicubic( sampler2D sampler, vec2 uv, float lod ) {
		vec2 fLodSize = vec2( textureSize( sampler, int( lod ) ) );
		vec2 cLodSize = vec2( textureSize( sampler, int( lod + 1.0 ) ) );
		vec2 fLodSizeInv = 1.0 / fLodSize;
		vec2 cLodSizeInv = 1.0 / cLodSize;
		vec4 fSample = bicubic( sampler, uv, vec4( fLodSizeInv, fLodSize ), floor( lod ) );
		vec4 cSample = bicubic( sampler, uv, vec4( cLodSizeInv, cLodSize ), ceil( lod ) );
		return mix( fSample, cSample, fract( lod ) );
	}
	vec3 getVolumeTransmissionRay( const in vec3 n, const in vec3 v, const in float thickness, const in float ior, const in mat4 modelMatrix ) {
		vec3 refractionVector = refract( - v, normalize( n ), 1.0 / ior );
		vec3 modelScale;
		modelScale.x = length( vec3( modelMatrix[ 0 ].xyz ) );
		modelScale.y = length( vec3( modelMatrix[ 1 ].xyz ) );
		modelScale.z = length( vec3( modelMatrix[ 2 ].xyz ) );
		return normalize( refractionVector ) * thickness * modelScale;
	}
	float applyIorToRoughness( const in float roughness, const in float ior ) {
		return roughness * clamp( ior * 2.0 - 2.0, 0.0, 1.0 );
	}
	vec4 getTransmissionSample( const in vec2 fragCoord, const in float roughness, const in float ior ) {
		float lod = log2( transmissionSamplerSize.x ) * applyIorToRoughness( roughness, ior );
		return textureBicubic( transmissionSamplerMap, fragCoord.xy, lod );
	}
	vec3 volumeAttenuation( const in float transmissionDistance, const in vec3 attenuationColor, const in float attenuationDistance ) {
		if ( isinf( attenuationDistance ) ) {
			return vec3( 1.0 );
		} else {
			vec3 attenuationCoefficient = -log( attenuationColor ) / attenuationDistance;
			vec3 transmittance = exp( - attenuationCoefficient * transmissionDistance );			return transmittance;
		}
	}
	vec4 getIBLVolumeRefraction( const in vec3 n, const in vec3 v, const in float roughness, const in vec3 diffuseColor,
		const in vec3 specularColor, const in float specularF90, const in vec3 position, const in mat4 modelMatrix,
		const in mat4 viewMatrix, const in mat4 projMatrix, const in float dispersion, const in float ior, const in float thickness,
		const in vec3 attenuationColor, const in float attenuationDistance ) {
		vec4 transmittedLight;
		vec3 transmittance;
		#ifdef USE_DISPERSION
			float halfSpread = ( ior - 1.0 ) * 0.025 * dispersion;
			vec3 iors = vec3( ior - halfSpread, ior, ior + halfSpread );
			for ( int i = 0; i < 3; i ++ ) {
				vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, iors[ i ], modelMatrix );
				vec3 refractedRayExit = position + transmissionRay;
				vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
				vec2 refractionCoords = ndcPos.xy / ndcPos.w;
				refractionCoords += 1.0;
				refractionCoords /= 2.0;
				vec4 transmissionSample = getTransmissionSample( refractionCoords, roughness, iors[ i ] );
				transmittedLight[ i ] = transmissionSample[ i ];
				transmittedLight.a += transmissionSample.a;
				transmittance[ i ] = diffuseColor[ i ] * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance )[ i ];
			}
			transmittedLight.a /= 3.0;
		#else
			vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, ior, modelMatrix );
			vec3 refractedRayExit = position + transmissionRay;
			vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
			vec2 refractionCoords = ndcPos.xy / ndcPos.w;
			refractionCoords += 1.0;
			refractionCoords /= 2.0;
			transmittedLight = getTransmissionSample( refractionCoords, roughness, ior );
			transmittance = diffuseColor * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance );
		#endif
		vec3 attenuatedColor = transmittance * transmittedLight.rgb;
		vec3 F = EnvironmentBRDF( n, v, specularColor, specularF90, roughness );
		float transmittanceFactor = ( transmittance.r + transmittance.g + transmittance.b ) / 3.0;
		return vec4( ( 1.0 - F ) * attenuatedColor, 1.0 - ( 1.0 - transmittedLight.a ) * transmittanceFactor );
	}
#endif`,x0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_SPECULARMAP
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,v0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	uniform mat3 mapTransform;
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	uniform mat3 alphaMapTransform;
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	uniform mat3 lightMapTransform;
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	uniform mat3 aoMapTransform;
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	uniform mat3 bumpMapTransform;
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	uniform mat3 normalMapTransform;
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_DISPLACEMENTMAP
	uniform mat3 displacementMapTransform;
	varying vec2 vDisplacementMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	uniform mat3 emissiveMapTransform;
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	uniform mat3 metalnessMapTransform;
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	uniform mat3 roughnessMapTransform;
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	uniform mat3 anisotropyMapTransform;
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	uniform mat3 clearcoatMapTransform;
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform mat3 clearcoatNormalMapTransform;
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform mat3 clearcoatRoughnessMapTransform;
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	uniform mat3 sheenColorMapTransform;
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	uniform mat3 sheenRoughnessMapTransform;
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	uniform mat3 iridescenceMapTransform;
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform mat3 iridescenceThicknessMapTransform;
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SPECULARMAP
	uniform mat3 specularMapTransform;
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	uniform mat3 specularColorMapTransform;
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	uniform mat3 specularIntensityMapTransform;
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,M0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	vUv = vec3( uv, 1 ).xy;
#endif
#ifdef USE_MAP
	vMapUv = ( mapTransform * vec3( MAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ALPHAMAP
	vAlphaMapUv = ( alphaMapTransform * vec3( ALPHAMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_LIGHTMAP
	vLightMapUv = ( lightMapTransform * vec3( LIGHTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_AOMAP
	vAoMapUv = ( aoMapTransform * vec3( AOMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_BUMPMAP
	vBumpMapUv = ( bumpMapTransform * vec3( BUMPMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_NORMALMAP
	vNormalMapUv = ( normalMapTransform * vec3( NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_DISPLACEMENTMAP
	vDisplacementMapUv = ( displacementMapTransform * vec3( DISPLACEMENTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_EMISSIVEMAP
	vEmissiveMapUv = ( emissiveMapTransform * vec3( EMISSIVEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_METALNESSMAP
	vMetalnessMapUv = ( metalnessMapTransform * vec3( METALNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ROUGHNESSMAP
	vRoughnessMapUv = ( roughnessMapTransform * vec3( ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ANISOTROPYMAP
	vAnisotropyMapUv = ( anisotropyMapTransform * vec3( ANISOTROPYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOATMAP
	vClearcoatMapUv = ( clearcoatMapTransform * vec3( CLEARCOATMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	vClearcoatNormalMapUv = ( clearcoatNormalMapTransform * vec3( CLEARCOAT_NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	vClearcoatRoughnessMapUv = ( clearcoatRoughnessMapTransform * vec3( CLEARCOAT_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCEMAP
	vIridescenceMapUv = ( iridescenceMapTransform * vec3( IRIDESCENCEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	vIridescenceThicknessMapUv = ( iridescenceThicknessMapTransform * vec3( IRIDESCENCE_THICKNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_COLORMAP
	vSheenColorMapUv = ( sheenColorMapTransform * vec3( SHEEN_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	vSheenRoughnessMapUv = ( sheenRoughnessMapTransform * vec3( SHEEN_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULARMAP
	vSpecularMapUv = ( specularMapTransform * vec3( SPECULARMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_COLORMAP
	vSpecularColorMapUv = ( specularColorMapTransform * vec3( SPECULAR_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	vSpecularIntensityMapUv = ( specularIntensityMapTransform * vec3( SPECULAR_INTENSITYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_TRANSMISSIONMAP
	vTransmissionMapUv = ( transmissionMapTransform * vec3( TRANSMISSIONMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_THICKNESSMAP
	vThicknessMapUv = ( thicknessMapTransform * vec3( THICKNESSMAP_UV, 1 ) ).xy;
#endif`,S0=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const y0=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,E0=`uniform sampler2D t2D;
uniform float backgroundIntensity;
varying vec2 vUv;
void main() {
	vec4 texColor = texture2D( t2D, vUv );
	#ifdef DECODE_VIDEO_TEXTURE
		texColor = vec4( mix( pow( texColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), texColor.rgb * 0.0773993808, vec3( lessThanEqual( texColor.rgb, vec3( 0.04045 ) ) ) ), texColor.w );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,T0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,b0=`#ifdef ENVMAP_TYPE_CUBE
	uniform samplerCube envMap;
#elif defined( ENVMAP_TYPE_CUBE_UV )
	uniform sampler2D envMap;
#endif
uniform float flipEnvMap;
uniform float backgroundBlurriness;
uniform float backgroundIntensity;
uniform mat3 backgroundRotation;
varying vec3 vWorldDirection;
#include <cube_uv_reflection_fragment>
void main() {
	#ifdef ENVMAP_TYPE_CUBE
		vec4 texColor = textureCube( envMap, backgroundRotation * vec3( flipEnvMap * vWorldDirection.x, vWorldDirection.yz ) );
	#elif defined( ENVMAP_TYPE_CUBE_UV )
		vec4 texColor = textureCubeUV( envMap, backgroundRotation * vWorldDirection, backgroundBlurriness );
	#else
		vec4 texColor = vec4( 0.0, 0.0, 0.0, 1.0 );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,A0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,w0=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,R0=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
varying vec2 vHighPrecisionZW;
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vHighPrecisionZW = gl_Position.zw;
}`,C0=`#if DEPTH_PACKING == 3200
	uniform float opacity;
#endif
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
varying vec2 vHighPrecisionZW;
void main() {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#if DEPTH_PACKING == 3200
		diffuseColor.a = opacity;
	#endif
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <logdepthbuf_fragment>
	#ifdef USE_REVERSED_DEPTH_BUFFER
		float fragCoordZ = vHighPrecisionZW[ 0 ] / vHighPrecisionZW[ 1 ];
	#else
		float fragCoordZ = 0.5 * vHighPrecisionZW[ 0 ] / vHighPrecisionZW[ 1 ] + 0.5;
	#endif
	#if DEPTH_PACKING == 3200
		gl_FragColor = vec4( vec3( 1.0 - fragCoordZ ), opacity );
	#elif DEPTH_PACKING == 3201
		gl_FragColor = packDepthToRGBA( fragCoordZ );
	#elif DEPTH_PACKING == 3202
		gl_FragColor = vec4( packDepthToRGB( fragCoordZ ), 1.0 );
	#elif DEPTH_PACKING == 3203
		gl_FragColor = vec4( packDepthToRG( fragCoordZ ), 0.0, 1.0 );
	#endif
}`,P0=`#define DISTANCE
varying vec3 vWorldPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <worldpos_vertex>
	#include <clipping_planes_vertex>
	vWorldPosition = worldPosition.xyz;
}`,D0=`#define DISTANCE
uniform vec3 referencePosition;
uniform float nearDistance;
uniform float farDistance;
varying vec3 vWorldPosition;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <clipping_planes_pars_fragment>
void main () {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	float dist = length( vWorldPosition - referencePosition );
	dist = ( dist - nearDistance ) / ( farDistance - nearDistance );
	dist = saturate( dist );
	gl_FragColor = vec4( dist, 0.0, 0.0, 1.0 );
}`,L0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,I0=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,U0=`uniform float scale;
attribute float lineDistance;
varying float vLineDistance;
#include <common>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	vLineDistance = scale * lineDistance;
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,N0=`uniform vec3 diffuse;
uniform float opacity;
uniform float dashSize;
uniform float totalSize;
varying float vLineDistance;
#include <common>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	if ( mod( vLineDistance, totalSize ) > dashSize ) {
		discard;
	}
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,F0=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#if defined ( USE_ENVMAP ) || defined ( USE_SKINNING )
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinbase_vertex>
		#include <skinnormal_vertex>
		#include <defaultnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <fog_vertex>
}`,O0=`uniform vec3 diffuse;
uniform float opacity;
#ifndef FLAT_SHADED
	varying vec3 vNormal;
#endif
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		reflectedLight.indirectDiffuse += lightMapTexel.rgb * lightMapIntensity * RECIPROCAL_PI;
	#else
		reflectedLight.indirectDiffuse += vec3( 1.0 );
	#endif
	#include <aomap_fragment>
	reflectedLight.indirectDiffuse *= diffuseColor.rgb;
	vec3 outgoingLight = reflectedLight.indirectDiffuse;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,B0=`#define LAMBERT
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,k0=`#define LAMBERT
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_lambert_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_lambert_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,z0=`#define MATCAP
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <displacementmap_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
	vViewPosition = - mvPosition.xyz;
}`,V0=`#define MATCAP
uniform vec3 diffuse;
uniform float opacity;
uniform sampler2D matcap;
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	vec3 viewDir = normalize( vViewPosition );
	vec3 x = normalize( vec3( viewDir.z, 0.0, - viewDir.x ) );
	vec3 y = cross( viewDir, x );
	vec2 uv = vec2( dot( x, normal ), dot( y, normal ) ) * 0.495 + 0.5;
	#ifdef USE_MATCAP
		vec4 matcapColor = texture2D( matcap, uv );
	#else
		vec4 matcapColor = vec4( vec3( mix( 0.2, 0.8, uv.y ) ), 1.0 );
	#endif
	vec3 outgoingLight = diffuseColor.rgb * matcapColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,G0=`#define NORMAL
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	vViewPosition = - mvPosition.xyz;
#endif
}`,H0=`#define NORMAL
uniform float opacity;
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <uv_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( 0.0, 0.0, 0.0, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	gl_FragColor = vec4( normalize( normal ) * 0.5 + 0.5, diffuseColor.a );
	#ifdef OPAQUE
		gl_FragColor.a = 1.0;
	#endif
}`,W0=`#define PHONG
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,X0=`#define PHONG
uniform vec3 diffuse;
uniform vec3 emissive;
uniform vec3 specular;
uniform float shininess;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_phong_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_phong_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,q0=`#define STANDARD
varying vec3 vViewPosition;
#ifdef USE_TRANSMISSION
	varying vec3 vWorldPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
#ifdef USE_TRANSMISSION
	vWorldPosition = worldPosition.xyz;
#endif
}`,Y0=`#define STANDARD
#ifdef PHYSICAL
	#define IOR
	#define USE_SPECULAR
#endif
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float roughness;
uniform float metalness;
uniform float opacity;
#ifdef IOR
	uniform float ior;
#endif
#ifdef USE_SPECULAR
	uniform float specularIntensity;
	uniform vec3 specularColor;
	#ifdef USE_SPECULAR_COLORMAP
		uniform sampler2D specularColorMap;
	#endif
	#ifdef USE_SPECULAR_INTENSITYMAP
		uniform sampler2D specularIntensityMap;
	#endif
#endif
#ifdef USE_CLEARCOAT
	uniform float clearcoat;
	uniform float clearcoatRoughness;
#endif
#ifdef USE_DISPERSION
	uniform float dispersion;
#endif
#ifdef USE_IRIDESCENCE
	uniform float iridescence;
	uniform float iridescenceIOR;
	uniform float iridescenceThicknessMinimum;
	uniform float iridescenceThicknessMaximum;
#endif
#ifdef USE_SHEEN
	uniform vec3 sheenColor;
	uniform float sheenRoughness;
	#ifdef USE_SHEEN_COLORMAP
		uniform sampler2D sheenColorMap;
	#endif
	#ifdef USE_SHEEN_ROUGHNESSMAP
		uniform sampler2D sheenRoughnessMap;
	#endif
#endif
#ifdef USE_ANISOTROPY
	uniform vec2 anisotropyVector;
	#ifdef USE_ANISOTROPYMAP
		uniform sampler2D anisotropyMap;
	#endif
#endif
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <iridescence_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_physical_pars_fragment>
#include <transmission_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <clearcoat_pars_fragment>
#include <iridescence_pars_fragment>
#include <roughnessmap_pars_fragment>
#include <metalnessmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <roughnessmap_fragment>
	#include <metalnessmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <clearcoat_normal_fragment_begin>
	#include <clearcoat_normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_physical_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 totalDiffuse = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse;
	vec3 totalSpecular = reflectedLight.directSpecular + reflectedLight.indirectSpecular;
	#include <transmission_fragment>
	vec3 outgoingLight = totalDiffuse + totalSpecular + totalEmissiveRadiance;
	#ifdef USE_SHEEN
 
		outgoingLight = outgoingLight + sheenSpecularDirect + sheenSpecularIndirect;
 
 	#endif
	#ifdef USE_CLEARCOAT
		float dotNVcc = saturate( dot( geometryClearcoatNormal, geometryViewDir ) );
		vec3 Fcc = F_Schlick( material.clearcoatF0, material.clearcoatF90, dotNVcc );
		outgoingLight = outgoingLight * ( 1.0 - material.clearcoat * Fcc ) + ( clearcoatSpecularDirect + clearcoatSpecularIndirect ) * material.clearcoat;
	#endif
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,$0=`#define TOON
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,K0=`#define TOON
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <gradientmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_toon_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_toon_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Z0=`uniform float size;
uniform float scale;
#include <common>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
#ifdef USE_POINTS_UV
	varying vec2 vUv;
	uniform mat3 uvTransform;
#endif
void main() {
	#ifdef USE_POINTS_UV
		vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	#endif
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	gl_PointSize = size;
	#ifdef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) gl_PointSize *= ( scale / - mvPosition.z );
	#endif
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <fog_vertex>
}`,J0=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <color_pars_fragment>
#include <map_particle_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_particle_fragment>
	#include <color_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,j0=`#include <common>
#include <batching_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <shadowmap_pars_vertex>
void main() {
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Q0=`uniform vec3 color;
uniform float opacity;
#include <common>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <logdepthbuf_pars_fragment>
#include <shadowmap_pars_fragment>
#include <shadowmask_pars_fragment>
void main() {
	#include <logdepthbuf_fragment>
	gl_FragColor = vec4( color, opacity * ( 1.0 - getShadowMask() ) );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,tx=`uniform float rotation;
uniform vec2 center;
#include <common>
#include <uv_pars_vertex>
#include <fog_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	vec4 mvPosition = modelViewMatrix[ 3 ];
	vec2 scale = vec2( length( modelMatrix[ 0 ].xyz ), length( modelMatrix[ 1 ].xyz ) );
	#ifndef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) scale *= - mvPosition.z;
	#endif
	vec2 alignedPosition = ( position.xy - ( center - vec2( 0.5 ) ) ) * scale;
	vec2 rotatedPosition;
	rotatedPosition.x = cos( rotation ) * alignedPosition.x - sin( rotation ) * alignedPosition.y;
	rotatedPosition.y = sin( rotation ) * alignedPosition.x + cos( rotation ) * alignedPosition.y;
	mvPosition.xy += rotatedPosition;
	gl_Position = projectionMatrix * mvPosition;
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,ex=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,Nt={alphahash_fragment:E_,alphahash_pars_fragment:T_,alphamap_fragment:b_,alphamap_pars_fragment:A_,alphatest_fragment:w_,alphatest_pars_fragment:R_,aomap_fragment:C_,aomap_pars_fragment:P_,batching_pars_vertex:D_,batching_vertex:L_,begin_vertex:I_,beginnormal_vertex:U_,bsdfs:N_,iridescence_fragment:F_,bumpmap_pars_fragment:O_,clipping_planes_fragment:B_,clipping_planes_pars_fragment:k_,clipping_planes_pars_vertex:z_,clipping_planes_vertex:V_,color_fragment:G_,color_pars_fragment:H_,color_pars_vertex:W_,color_vertex:X_,common:q_,cube_uv_reflection_fragment:Y_,defaultnormal_vertex:$_,displacementmap_pars_vertex:K_,displacementmap_vertex:Z_,emissivemap_fragment:J_,emissivemap_pars_fragment:j_,colorspace_fragment:Q_,colorspace_pars_fragment:tg,envmap_fragment:eg,envmap_common_pars_fragment:ng,envmap_pars_fragment:ig,envmap_pars_vertex:rg,envmap_physical_pars_fragment:mg,envmap_vertex:sg,fog_vertex:ag,fog_pars_vertex:og,fog_fragment:lg,fog_pars_fragment:cg,gradientmap_pars_fragment:ug,lightmap_pars_fragment:fg,lights_lambert_fragment:hg,lights_lambert_pars_fragment:dg,lights_pars_begin:pg,lights_toon_fragment:_g,lights_toon_pars_fragment:gg,lights_phong_fragment:xg,lights_phong_pars_fragment:vg,lights_physical_fragment:Mg,lights_physical_pars_fragment:Sg,lights_fragment_begin:yg,lights_fragment_maps:Eg,lights_fragment_end:Tg,logdepthbuf_fragment:bg,logdepthbuf_pars_fragment:Ag,logdepthbuf_pars_vertex:wg,logdepthbuf_vertex:Rg,map_fragment:Cg,map_pars_fragment:Pg,map_particle_fragment:Dg,map_particle_pars_fragment:Lg,metalnessmap_fragment:Ig,metalnessmap_pars_fragment:Ug,morphinstance_vertex:Ng,morphcolor_vertex:Fg,morphnormal_vertex:Og,morphtarget_pars_vertex:Bg,morphtarget_vertex:kg,normal_fragment_begin:zg,normal_fragment_maps:Vg,normal_pars_fragment:Gg,normal_pars_vertex:Hg,normal_vertex:Wg,normalmap_pars_fragment:Xg,clearcoat_normal_fragment_begin:qg,clearcoat_normal_fragment_maps:Yg,clearcoat_pars_fragment:$g,iridescence_pars_fragment:Kg,opaque_fragment:Zg,packing:Jg,premultiplied_alpha_fragment:jg,project_vertex:Qg,dithering_fragment:t0,dithering_pars_fragment:e0,roughnessmap_fragment:n0,roughnessmap_pars_fragment:i0,shadowmap_pars_fragment:r0,shadowmap_pars_vertex:s0,shadowmap_vertex:a0,shadowmask_pars_fragment:o0,skinbase_vertex:l0,skinning_pars_vertex:c0,skinning_vertex:u0,skinnormal_vertex:f0,specularmap_fragment:h0,specularmap_pars_fragment:d0,tonemapping_fragment:p0,tonemapping_pars_fragment:m0,transmission_fragment:_0,transmission_pars_fragment:g0,uv_pars_fragment:x0,uv_pars_vertex:v0,uv_vertex:M0,worldpos_vertex:S0,background_vert:y0,background_frag:E0,backgroundCube_vert:T0,backgroundCube_frag:b0,cube_vert:A0,cube_frag:w0,depth_vert:R0,depth_frag:C0,distance_vert:P0,distance_frag:D0,equirect_vert:L0,equirect_frag:I0,linedashed_vert:U0,linedashed_frag:N0,meshbasic_vert:F0,meshbasic_frag:O0,meshlambert_vert:B0,meshlambert_frag:k0,meshmatcap_vert:z0,meshmatcap_frag:V0,meshnormal_vert:G0,meshnormal_frag:H0,meshphong_vert:W0,meshphong_frag:X0,meshphysical_vert:q0,meshphysical_frag:Y0,meshtoon_vert:$0,meshtoon_frag:K0,points_vert:Z0,points_frag:J0,shadow_vert:j0,shadow_frag:Q0,sprite_vert:tx,sprite_frag:ex},ct={common:{diffuse:{value:new Zt(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new It},alphaMap:{value:null},alphaMapTransform:{value:new It},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new It}},envmap:{envMap:{value:null},envMapRotation:{value:new It},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98},dfgLUT:{value:null}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new It}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new It}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new It},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new It},normalScale:{value:new Qt(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new It},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new It}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new It}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new It}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new Zt(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new Zt(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new It},alphaTest:{value:0},uvTransform:{value:new It}},sprite:{diffuse:{value:new Zt(16777215)},opacity:{value:1},center:{value:new Qt(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new It},alphaMap:{value:null},alphaMapTransform:{value:new It},alphaTest:{value:0}}},Tn={basic:{uniforms:Ne([ct.common,ct.specularmap,ct.envmap,ct.aomap,ct.lightmap,ct.fog]),vertexShader:Nt.meshbasic_vert,fragmentShader:Nt.meshbasic_frag},lambert:{uniforms:Ne([ct.common,ct.specularmap,ct.envmap,ct.aomap,ct.lightmap,ct.emissivemap,ct.bumpmap,ct.normalmap,ct.displacementmap,ct.fog,ct.lights,{emissive:{value:new Zt(0)},envMapIntensity:{value:1}}]),vertexShader:Nt.meshlambert_vert,fragmentShader:Nt.meshlambert_frag},phong:{uniforms:Ne([ct.common,ct.specularmap,ct.envmap,ct.aomap,ct.lightmap,ct.emissivemap,ct.bumpmap,ct.normalmap,ct.displacementmap,ct.fog,ct.lights,{emissive:{value:new Zt(0)},specular:{value:new Zt(1118481)},shininess:{value:30},envMapIntensity:{value:1}}]),vertexShader:Nt.meshphong_vert,fragmentShader:Nt.meshphong_frag},standard:{uniforms:Ne([ct.common,ct.envmap,ct.aomap,ct.lightmap,ct.emissivemap,ct.bumpmap,ct.normalmap,ct.displacementmap,ct.roughnessmap,ct.metalnessmap,ct.fog,ct.lights,{emissive:{value:new Zt(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:Nt.meshphysical_vert,fragmentShader:Nt.meshphysical_frag},toon:{uniforms:Ne([ct.common,ct.aomap,ct.lightmap,ct.emissivemap,ct.bumpmap,ct.normalmap,ct.displacementmap,ct.gradientmap,ct.fog,ct.lights,{emissive:{value:new Zt(0)}}]),vertexShader:Nt.meshtoon_vert,fragmentShader:Nt.meshtoon_frag},matcap:{uniforms:Ne([ct.common,ct.bumpmap,ct.normalmap,ct.displacementmap,ct.fog,{matcap:{value:null}}]),vertexShader:Nt.meshmatcap_vert,fragmentShader:Nt.meshmatcap_frag},points:{uniforms:Ne([ct.points,ct.fog]),vertexShader:Nt.points_vert,fragmentShader:Nt.points_frag},dashed:{uniforms:Ne([ct.common,ct.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:Nt.linedashed_vert,fragmentShader:Nt.linedashed_frag},depth:{uniforms:Ne([ct.common,ct.displacementmap]),vertexShader:Nt.depth_vert,fragmentShader:Nt.depth_frag},normal:{uniforms:Ne([ct.common,ct.bumpmap,ct.normalmap,ct.displacementmap,{opacity:{value:1}}]),vertexShader:Nt.meshnormal_vert,fragmentShader:Nt.meshnormal_frag},sprite:{uniforms:Ne([ct.sprite,ct.fog]),vertexShader:Nt.sprite_vert,fragmentShader:Nt.sprite_frag},background:{uniforms:{uvTransform:{value:new It},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:Nt.background_vert,fragmentShader:Nt.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new It}},vertexShader:Nt.backgroundCube_vert,fragmentShader:Nt.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:Nt.cube_vert,fragmentShader:Nt.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:Nt.equirect_vert,fragmentShader:Nt.equirect_frag},distance:{uniforms:Ne([ct.common,ct.displacementmap,{referencePosition:{value:new W},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:Nt.distance_vert,fragmentShader:Nt.distance_frag},shadow:{uniforms:Ne([ct.lights,ct.fog,{color:{value:new Zt(0)},opacity:{value:1}}]),vertexShader:Nt.shadow_vert,fragmentShader:Nt.shadow_frag}};Tn.physical={uniforms:Ne([Tn.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new It},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new It},clearcoatNormalScale:{value:new Qt(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new It},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new It},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new It},sheen:{value:0},sheenColor:{value:new Zt(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new It},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new It},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new It},transmissionSamplerSize:{value:new Qt},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new It},attenuationDistance:{value:0},attenuationColor:{value:new Zt(0)},specularColor:{value:new Zt(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new It},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new It},anisotropyVector:{value:new Qt},anisotropyMap:{value:null},anisotropyMapTransform:{value:new It}}]),vertexShader:Nt.meshphysical_vert,fragmentShader:Nt.meshphysical_frag};const js={r:0,b:0,g:0},Ni=new ii,nx=new ve;function ix(i,t,e,n,r,s){const a=new Zt(0);let o=r===!0?0:1,l,c,u=null,h=0,f=null;function d(M){let T=M.isScene===!0?M.background:null;if(T&&T.isTexture){const S=M.backgroundBlurriness>0;T=t.get(T,S)}return T}function _(M){let T=!1;const S=d(M);S===null?p(a,o):S&&S.isColor&&(p(S,1),T=!0);const b=i.xr.getEnvironmentBlendMode();b==="additive"?e.buffers.color.setClear(0,0,0,1,s):b==="alpha-blend"&&e.buffers.color.setClear(0,0,0,0,s),(i.autoClear||T)&&(e.buffers.depth.setTest(!0),e.buffers.depth.setMask(!0),e.buffers.color.setMask(!0),i.clear(i.autoClearColor,i.autoClearDepth,i.autoClearStencil))}function g(M,T){const S=d(T);S&&(S.isCubeTexture||S.mapping===Oa)?(c===void 0&&(c=new Nn(new Ts(1,1,1),new Fn({name:"BackgroundCubeMaterial",uniforms:Nr(Tn.backgroundCube.uniforms),vertexShader:Tn.backgroundCube.vertexShader,fragmentShader:Tn.backgroundCube.fragmentShader,side:We,depthTest:!1,depthWrite:!1,fog:!1,allowOverride:!1})),c.geometry.deleteAttribute("normal"),c.geometry.deleteAttribute("uv"),c.onBeforeRender=function(b,A,R){this.matrixWorld.copyPosition(R.matrixWorld)},Object.defineProperty(c.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),n.update(c)),Ni.copy(T.backgroundRotation),Ni.x*=-1,Ni.y*=-1,Ni.z*=-1,S.isCubeTexture&&S.isRenderTargetTexture===!1&&(Ni.y*=-1,Ni.z*=-1),c.material.uniforms.envMap.value=S,c.material.uniforms.flipEnvMap.value=S.isCubeTexture&&S.isRenderTargetTexture===!1?-1:1,c.material.uniforms.backgroundBlurriness.value=T.backgroundBlurriness,c.material.uniforms.backgroundIntensity.value=T.backgroundIntensity,c.material.uniforms.backgroundRotation.value.setFromMatrix4(nx.makeRotationFromEuler(Ni)),c.material.toneMapped=Ht.getTransfer(S.colorSpace)!==Kt,(u!==S||h!==S.version||f!==i.toneMapping)&&(c.material.needsUpdate=!0,u=S,h=S.version,f=i.toneMapping),c.layers.enableAll(),M.unshift(c,c.geometry,c.material,0,0,null)):S&&S.isTexture&&(l===void 0&&(l=new Nn(new bs(2,2),new Fn({name:"BackgroundMaterial",uniforms:Nr(Tn.background.uniforms),vertexShader:Tn.background.vertexShader,fragmentShader:Tn.background.fragmentShader,side:bi,depthTest:!1,depthWrite:!1,fog:!1,allowOverride:!1})),l.geometry.deleteAttribute("normal"),Object.defineProperty(l.material,"map",{get:function(){return this.uniforms.t2D.value}}),n.update(l)),l.material.uniforms.t2D.value=S,l.material.uniforms.backgroundIntensity.value=T.backgroundIntensity,l.material.toneMapped=Ht.getTransfer(S.colorSpace)!==Kt,S.matrixAutoUpdate===!0&&S.updateMatrix(),l.material.uniforms.uvTransform.value.copy(S.matrix),(u!==S||h!==S.version||f!==i.toneMapping)&&(l.material.needsUpdate=!0,u=S,h=S.version,f=i.toneMapping),l.layers.enableAll(),M.unshift(l,l.geometry,l.material,0,0,null))}function p(M,T){M.getRGB(js,Zh(i)),e.buffers.color.setClear(js.r,js.g,js.b,T,s)}function m(){c!==void 0&&(c.geometry.dispose(),c.material.dispose(),c=void 0),l!==void 0&&(l.geometry.dispose(),l.material.dispose(),l=void 0)}return{getClearColor:function(){return a},setClearColor:function(M,T=1){a.set(M),o=T,p(a,o)},getClearAlpha:function(){return o},setClearAlpha:function(M){o=M,p(a,o)},render:_,addToRenderList:g,dispose:m}}function rx(i,t){const e=i.getParameter(i.MAX_VERTEX_ATTRIBS),n={},r=f(null);let s=r,a=!1;function o(D,B,k,X,C){let L=!1;const P=h(D,X,k,B);s!==P&&(s=P,c(s.object)),L=d(D,X,k,C),L&&_(D,X,k,C),C!==null&&t.update(C,i.ELEMENT_ARRAY_BUFFER),(L||a)&&(a=!1,S(D,B,k,X),C!==null&&i.bindBuffer(i.ELEMENT_ARRAY_BUFFER,t.get(C).buffer))}function l(){return i.createVertexArray()}function c(D){return i.bindVertexArray(D)}function u(D){return i.deleteVertexArray(D)}function h(D,B,k,X){const C=X.wireframe===!0;let L=n[B.id];L===void 0&&(L={},n[B.id]=L);const P=D.isInstancedMesh===!0?D.id:0;let z=L[P];z===void 0&&(z={},L[P]=z);let O=z[k.id];O===void 0&&(O={},z[k.id]=O);let J=O[C];return J===void 0&&(J=f(l()),O[C]=J),J}function f(D){const B=[],k=[],X=[];for(let C=0;C<e;C++)B[C]=0,k[C]=0,X[C]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:B,enabledAttributes:k,attributeDivisors:X,object:D,attributes:{},index:null}}function d(D,B,k,X){const C=s.attributes,L=B.attributes;let P=0;const z=k.getAttributes();for(const O in z)if(z[O].location>=0){const Q=C[O];let st=L[O];if(st===void 0&&(O==="instanceMatrix"&&D.instanceMatrix&&(st=D.instanceMatrix),O==="instanceColor"&&D.instanceColor&&(st=D.instanceColor)),Q===void 0||Q.attribute!==st||st&&Q.data!==st.data)return!0;P++}return s.attributesNum!==P||s.index!==X}function _(D,B,k,X){const C={},L=B.attributes;let P=0;const z=k.getAttributes();for(const O in z)if(z[O].location>=0){let Q=L[O];Q===void 0&&(O==="instanceMatrix"&&D.instanceMatrix&&(Q=D.instanceMatrix),O==="instanceColor"&&D.instanceColor&&(Q=D.instanceColor));const st={};st.attribute=Q,Q&&Q.data&&(st.data=Q.data),C[O]=st,P++}s.attributes=C,s.attributesNum=P,s.index=X}function g(){const D=s.newAttributes;for(let B=0,k=D.length;B<k;B++)D[B]=0}function p(D){m(D,0)}function m(D,B){const k=s.newAttributes,X=s.enabledAttributes,C=s.attributeDivisors;k[D]=1,X[D]===0&&(i.enableVertexAttribArray(D),X[D]=1),C[D]!==B&&(i.vertexAttribDivisor(D,B),C[D]=B)}function M(){const D=s.newAttributes,B=s.enabledAttributes;for(let k=0,X=B.length;k<X;k++)B[k]!==D[k]&&(i.disableVertexAttribArray(k),B[k]=0)}function T(D,B,k,X,C,L,P){P===!0?i.vertexAttribIPointer(D,B,k,C,L):i.vertexAttribPointer(D,B,k,X,C,L)}function S(D,B,k,X){g();const C=X.attributes,L=k.getAttributes(),P=B.defaultAttributeValues;for(const z in L){const O=L[z];if(O.location>=0){let J=C[z];if(J===void 0&&(z==="instanceMatrix"&&D.instanceMatrix&&(J=D.instanceMatrix),z==="instanceColor"&&D.instanceColor&&(J=D.instanceColor)),J!==void 0){const Q=J.normalized,st=J.itemSize,bt=t.get(J);if(bt===void 0)continue;const Ut=bt.buffer,Ft=bt.type,K=bt.bytesPerElement,nt=Ft===i.INT||Ft===i.UNSIGNED_INT||J.gpuType===vc;if(J.isInterleavedBufferAttribute){const lt=J.data,Lt=lt.stride,At=J.offset;if(lt.isInstancedInterleavedBuffer){for(let Rt=0;Rt<O.locationSize;Rt++)m(O.location+Rt,lt.meshPerAttribute);D.isInstancedMesh!==!0&&X._maxInstanceCount===void 0&&(X._maxInstanceCount=lt.meshPerAttribute*lt.count)}else for(let Rt=0;Rt<O.locationSize;Rt++)p(O.location+Rt);i.bindBuffer(i.ARRAY_BUFFER,Ut);for(let Rt=0;Rt<O.locationSize;Rt++)T(O.location+Rt,st/O.locationSize,Ft,Q,Lt*K,(At+st/O.locationSize*Rt)*K,nt)}else{if(J.isInstancedBufferAttribute){for(let lt=0;lt<O.locationSize;lt++)m(O.location+lt,J.meshPerAttribute);D.isInstancedMesh!==!0&&X._maxInstanceCount===void 0&&(X._maxInstanceCount=J.meshPerAttribute*J.count)}else for(let lt=0;lt<O.locationSize;lt++)p(O.location+lt);i.bindBuffer(i.ARRAY_BUFFER,Ut);for(let lt=0;lt<O.locationSize;lt++)T(O.location+lt,st/O.locationSize,Ft,Q,st*K,st/O.locationSize*lt*K,nt)}}else if(P!==void 0){const Q=P[z];if(Q!==void 0)switch(Q.length){case 2:i.vertexAttrib2fv(O.location,Q);break;case 3:i.vertexAttrib3fv(O.location,Q);break;case 4:i.vertexAttrib4fv(O.location,Q);break;default:i.vertexAttrib1fv(O.location,Q)}}}}M()}function b(){y();for(const D in n){const B=n[D];for(const k in B){const X=B[k];for(const C in X){const L=X[C];for(const P in L)u(L[P].object),delete L[P];delete X[C]}}delete n[D]}}function A(D){if(n[D.id]===void 0)return;const B=n[D.id];for(const k in B){const X=B[k];for(const C in X){const L=X[C];for(const P in L)u(L[P].object),delete L[P];delete X[C]}}delete n[D.id]}function R(D){for(const B in n){const k=n[B];for(const X in k){const C=k[X];if(C[D.id]===void 0)continue;const L=C[D.id];for(const P in L)u(L[P].object),delete L[P];delete C[D.id]}}}function x(D){for(const B in n){const k=n[B],X=D.isInstancedMesh===!0?D.id:0,C=k[X];if(C!==void 0){for(const L in C){const P=C[L];for(const z in P)u(P[z].object),delete P[z];delete C[L]}delete k[X],Object.keys(k).length===0&&delete n[B]}}}function y(){G(),a=!0,s!==r&&(s=r,c(s.object))}function G(){r.geometry=null,r.program=null,r.wireframe=!1}return{setup:o,reset:y,resetDefaultState:G,dispose:b,releaseStatesOfGeometry:A,releaseStatesOfObject:x,releaseStatesOfProgram:R,initAttributes:g,enableAttribute:p,disableUnusedAttributes:M}}function sx(i,t,e){let n;function r(c){n=c}function s(c,u){i.drawArrays(n,c,u),e.update(u,n,1)}function a(c,u,h){h!==0&&(i.drawArraysInstanced(n,c,u,h),e.update(u,n,h))}function o(c,u,h){if(h===0)return;t.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,c,0,u,0,h);let d=0;for(let _=0;_<h;_++)d+=u[_];e.update(d,n,1)}function l(c,u,h,f){if(h===0)return;const d=t.get("WEBGL_multi_draw");if(d===null)for(let _=0;_<c.length;_++)a(c[_],u[_],f[_]);else{d.multiDrawArraysInstancedWEBGL(n,c,0,u,0,f,0,h);let _=0;for(let g=0;g<h;g++)_+=u[g]*f[g];e.update(_,n,1)}}this.setMode=r,this.render=s,this.renderInstances=a,this.renderMultiDraw=o,this.renderMultiDrawInstances=l}function ax(i,t,e,n){let r;function s(){if(r!==void 0)return r;if(t.has("EXT_texture_filter_anisotropic")===!0){const R=t.get("EXT_texture_filter_anisotropic");r=i.getParameter(R.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else r=0;return r}function a(R){return!(R!==xn&&n.convert(R)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_FORMAT))}function o(R){const x=R===ei&&(t.has("EXT_color_buffer_half_float")||t.has("EXT_color_buffer_float"));return!(R!==cn&&n.convert(R)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_TYPE)&&R!==wn&&!x)}function l(R){if(R==="highp"){if(i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.HIGH_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.HIGH_FLOAT).precision>0)return"highp";R="mediump"}return R==="mediump"&&i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.MEDIUM_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let c=e.precision!==void 0?e.precision:"highp";const u=l(c);u!==c&&(Pt("WebGLRenderer:",c,"not supported, using",u,"instead."),c=u);const h=e.logarithmicDepthBuffer===!0,f=e.reversedDepthBuffer===!0&&t.has("EXT_clip_control"),d=i.getParameter(i.MAX_TEXTURE_IMAGE_UNITS),_=i.getParameter(i.MAX_VERTEX_TEXTURE_IMAGE_UNITS),g=i.getParameter(i.MAX_TEXTURE_SIZE),p=i.getParameter(i.MAX_CUBE_MAP_TEXTURE_SIZE),m=i.getParameter(i.MAX_VERTEX_ATTRIBS),M=i.getParameter(i.MAX_VERTEX_UNIFORM_VECTORS),T=i.getParameter(i.MAX_VARYING_VECTORS),S=i.getParameter(i.MAX_FRAGMENT_UNIFORM_VECTORS),b=i.getParameter(i.MAX_SAMPLES),A=i.getParameter(i.SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:s,getMaxPrecision:l,textureFormatReadable:a,textureTypeReadable:o,precision:c,logarithmicDepthBuffer:h,reversedDepthBuffer:f,maxTextures:d,maxVertexTextures:_,maxTextureSize:g,maxCubemapSize:p,maxAttributes:m,maxVertexUniforms:M,maxVaryings:T,maxFragmentUniforms:S,maxSamples:b,samples:A}}function ox(i){const t=this;let e=null,n=0,r=!1,s=!1;const a=new Bi,o=new It,l={value:null,needsUpdate:!1};this.uniform=l,this.numPlanes=0,this.numIntersection=0,this.init=function(h,f){const d=h.length!==0||f||n!==0||r;return r=f,n=h.length,d},this.beginShadows=function(){s=!0,u(null)},this.endShadows=function(){s=!1},this.setGlobalState=function(h,f){e=u(h,f,0)},this.setState=function(h,f,d){const _=h.clippingPlanes,g=h.clipIntersection,p=h.clipShadows,m=i.get(h);if(!r||_===null||_.length===0||s&&!p)s?u(null):c();else{const M=s?0:n,T=M*4;let S=m.clippingState||null;l.value=S,S=u(_,f,T,d);for(let b=0;b!==T;++b)S[b]=e[b];m.clippingState=S,this.numIntersection=g?this.numPlanes:0,this.numPlanes+=M}};function c(){l.value!==e&&(l.value=e,l.needsUpdate=n>0),t.numPlanes=n,t.numIntersection=0}function u(h,f,d,_){const g=h!==null?h.length:0;let p=null;if(g!==0){if(p=l.value,_!==!0||p===null){const m=d+g*4,M=f.matrixWorldInverse;o.getNormalMatrix(M),(p===null||p.length<m)&&(p=new Float32Array(m));for(let T=0,S=d;T!==g;++T,S+=4)a.copy(h[T]).applyMatrix4(M,o),a.normal.toArray(p,S),p[S+3]=a.constant}l.value=p,l.needsUpdate=!0}return t.numPlanes=g,t.numIntersection=0,p}}const vi=4,Nu=[.125,.215,.35,.446,.526,.582],Vi=20,lx=256,Yr=new jh,Fu=new Zt;let Ro=null,Co=0,Po=0,Do=!1;const cx=new W;class Ou{constructor(t){this._renderer=t,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._sizeLods=[],this._sigmas=[],this._lodMeshes=[],this._backgroundBox=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._blurMaterial=null,this._ggxMaterial=null}fromScene(t,e=0,n=.1,r=100,s={}){const{size:a=256,position:o=cx}=s;Ro=this._renderer.getRenderTarget(),Co=this._renderer.getActiveCubeFace(),Po=this._renderer.getActiveMipmapLevel(),Do=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(a);const l=this._allocateTargets();return l.depthBuffer=!0,this._sceneToCubeUV(t,n,r,l,o),e>0&&this._blur(l,0,0,e),this._applyPMREM(l),this._cleanup(l),l}fromEquirectangular(t,e=null){return this._fromTexture(t,e)}fromCubemap(t,e=null){return this._fromTexture(t,e)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=zu(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=ku(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose(),this._backgroundBox!==null&&(this._backgroundBox.geometry.dispose(),this._backgroundBox.material.dispose())}_setSize(t){this._lodMax=Math.floor(Math.log2(t)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._ggxMaterial!==null&&this._ggxMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let t=0;t<this._lodMeshes.length;t++)this._lodMeshes[t].geometry.dispose()}_cleanup(t){this._renderer.setRenderTarget(Ro,Co,Po),this._renderer.xr.enabled=Do,t.scissorTest=!1,_r(t,0,0,t.width,t.height)}_fromTexture(t,e){t.mapping===Ji||t.mapping===Lr?this._setSize(t.image.length===0?16:t.image[0].width||t.image[0].image.width):this._setSize(t.image.width/4),Ro=this._renderer.getRenderTarget(),Co=this._renderer.getActiveCubeFace(),Po=this._renderer.getActiveMipmapLevel(),Do=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=e||this._allocateTargets();return this._textureToCubeUV(t,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const t=3*Math.max(this._cubeSize,112),e=4*this._cubeSize,n={magFilter:Ie,minFilter:Ie,generateMipmaps:!1,type:ei,format:xn,colorSpace:Ur,depthBuffer:!1},r=Bu(t,e,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==t||this._pingPongRenderTarget.height!==e){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=Bu(t,e,n);const{_lodMax:s}=this;({lodMeshes:this._lodMeshes,sizeLods:this._sizeLods,sigmas:this._sigmas}=ux(s)),this._blurMaterial=hx(s,t,e),this._ggxMaterial=fx(s,t,e)}return r}_compileMaterial(t){const e=new Nn(new si,t);this._renderer.compile(e,Yr)}_sceneToCubeUV(t,e,n,r,s){const l=new ln(90,1,e,n),c=[1,-1,1,1,1,1],u=[1,1,1,-1,-1,-1],h=this._renderer,f=h.autoClear,d=h.toneMapping;h.getClearColor(Fu),h.toneMapping=Cn,h.autoClear=!1,h.state.buffers.depth.getReversed()&&(h.setRenderTarget(r),h.clearDepth(),h.setRenderTarget(null)),this._backgroundBox===null&&(this._backgroundBox=new Nn(new Ts,new Cc({name:"PMREM.Background",side:We,depthWrite:!1,depthTest:!1})));const g=this._backgroundBox,p=g.material;let m=!1;const M=t.background;M?M.isColor&&(p.color.copy(M),t.background=null,m=!0):(p.color.copy(Fu),m=!0);for(let T=0;T<6;T++){const S=T%3;S===0?(l.up.set(0,c[T],0),l.position.set(s.x,s.y,s.z),l.lookAt(s.x+u[T],s.y,s.z)):S===1?(l.up.set(0,0,c[T]),l.position.set(s.x,s.y,s.z),l.lookAt(s.x,s.y+u[T],s.z)):(l.up.set(0,c[T],0),l.position.set(s.x,s.y,s.z),l.lookAt(s.x,s.y,s.z+u[T]));const b=this._cubeSize;_r(r,S*b,T>2?b:0,b,b),h.setRenderTarget(r),m&&h.render(g,l),h.render(t,l)}h.toneMapping=d,h.autoClear=f,t.background=M}_textureToCubeUV(t,e){const n=this._renderer,r=t.mapping===Ji||t.mapping===Lr;r?(this._cubemapMaterial===null&&(this._cubemapMaterial=zu()),this._cubemapMaterial.uniforms.flipEnvMap.value=t.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=ku());const s=r?this._cubemapMaterial:this._equirectMaterial,a=this._lodMeshes[0];a.material=s;const o=s.uniforms;o.envMap.value=t;const l=this._cubeSize;_r(e,0,0,3*l,2*l),n.setRenderTarget(e),n.render(a,Yr)}_applyPMREM(t){const e=this._renderer,n=e.autoClear;e.autoClear=!1;const r=this._lodMeshes.length;for(let s=1;s<r;s++)this._applyGGXFilter(t,s-1,s);e.autoClear=n}_applyGGXFilter(t,e,n){const r=this._renderer,s=this._pingPongRenderTarget,a=this._ggxMaterial,o=this._lodMeshes[n];o.material=a;const l=a.uniforms,c=n/(this._lodMeshes.length-1),u=e/(this._lodMeshes.length-1),h=Math.sqrt(c*c-u*u),f=0+c*1.25,d=h*f,{_lodMax:_}=this,g=this._sizeLods[n],p=3*g*(n>_-vi?n-_+vi:0),m=4*(this._cubeSize-g);l.envMap.value=t.texture,l.roughness.value=d,l.mipInt.value=_-e,_r(s,p,m,3*g,2*g),r.setRenderTarget(s),r.render(o,Yr),l.envMap.value=s.texture,l.roughness.value=0,l.mipInt.value=_-n,_r(t,p,m,3*g,2*g),r.setRenderTarget(t),r.render(o,Yr)}_blur(t,e,n,r,s){const a=this._pingPongRenderTarget;this._halfBlur(t,a,e,n,r,"latitudinal",s),this._halfBlur(a,t,n,n,r,"longitudinal",s)}_halfBlur(t,e,n,r,s,a,o){const l=this._renderer,c=this._blurMaterial;a!=="latitudinal"&&a!=="longitudinal"&&Xt("blur direction must be either latitudinal or longitudinal!");const u=3,h=this._lodMeshes[r];h.material=c;const f=c.uniforms,d=this._sizeLods[n]-1,_=isFinite(s)?Math.PI/(2*d):2*Math.PI/(2*Vi-1),g=s/_,p=isFinite(s)?1+Math.floor(u*g):Vi;p>Vi&&Pt(`sigmaRadians, ${s}, is too large and will clip, as it requested ${p} samples when the maximum is set to ${Vi}`);const m=[];let M=0;for(let R=0;R<Vi;++R){const x=R/g,y=Math.exp(-x*x/2);m.push(y),R===0?M+=y:R<p&&(M+=2*y)}for(let R=0;R<m.length;R++)m[R]=m[R]/M;f.envMap.value=t.texture,f.samples.value=p,f.weights.value=m,f.latitudinal.value=a==="latitudinal",o&&(f.poleAxis.value=o);const{_lodMax:T}=this;f.dTheta.value=_,f.mipInt.value=T-n;const S=this._sizeLods[r],b=3*S*(r>T-vi?r-T+vi:0),A=4*(this._cubeSize-S);_r(e,b,A,3*S,2*S),l.setRenderTarget(e),l.render(h,Yr)}}function ux(i){const t=[],e=[],n=[];let r=i;const s=i-vi+1+Nu.length;for(let a=0;a<s;a++){const o=Math.pow(2,r);t.push(o);let l=1/o;a>i-vi?l=Nu[a-i+vi-1]:a===0&&(l=0),e.push(l);const c=1/(o-2),u=-c,h=1+c,f=[u,u,h,u,h,h,u,u,h,h,u,h],d=6,_=6,g=3,p=2,m=1,M=new Float32Array(g*_*d),T=new Float32Array(p*_*d),S=new Float32Array(m*_*d);for(let A=0;A<d;A++){const R=A%3*2/3-1,x=A>2?0:-1,y=[R,x,0,R+2/3,x,0,R+2/3,x+1,0,R,x,0,R+2/3,x+1,0,R,x+1,0];M.set(y,g*_*A),T.set(f,p*_*A);const G=[A,A,A,A,A,A];S.set(G,m*_*A)}const b=new si;b.setAttribute("position",new Dn(M,g)),b.setAttribute("uv",new Dn(T,p)),b.setAttribute("faceIndex",new Dn(S,m)),n.push(new Nn(b,null)),r>vi&&r--}return{lodMeshes:n,sizeLods:t,sigmas:e}}function Bu(i,t,e){const n=new Pn(i,t,e);return n.texture.mapping=Oa,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function _r(i,t,e,n,r){i.viewport.set(t,e,n,r),i.scissor.set(t,e,n,r)}function fx(i,t,e){return new Fn({name:"PMREMGGXConvolution",defines:{GGX_SAMPLES:lx,CUBEUV_TEXEL_WIDTH:1/t,CUBEUV_TEXEL_HEIGHT:1/e,CUBEUV_MAX_MIP:`${i}.0`},uniforms:{envMap:{value:null},roughness:{value:0},mipInt:{value:0}},vertexShader:ka(),fragmentShader:`

			precision highp float;
			precision highp int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform float roughness;
			uniform float mipInt;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			#define PI 3.14159265359

			// Van der Corput radical inverse
			float radicalInverse_VdC(uint bits) {
				bits = (bits << 16u) | (bits >> 16u);
				bits = ((bits & 0x55555555u) << 1u) | ((bits & 0xAAAAAAAAu) >> 1u);
				bits = ((bits & 0x33333333u) << 2u) | ((bits & 0xCCCCCCCCu) >> 2u);
				bits = ((bits & 0x0F0F0F0Fu) << 4u) | ((bits & 0xF0F0F0F0u) >> 4u);
				bits = ((bits & 0x00FF00FFu) << 8u) | ((bits & 0xFF00FF00u) >> 8u);
				return float(bits) * 2.3283064365386963e-10; // / 0x100000000
			}

			// Hammersley sequence
			vec2 hammersley(uint i, uint N) {
				return vec2(float(i) / float(N), radicalInverse_VdC(i));
			}

			// GGX VNDF importance sampling (Eric Heitz 2018)
			// "Sampling the GGX Distribution of Visible Normals"
			// https://jcgt.org/published/0007/04/01/
			vec3 importanceSampleGGX_VNDF(vec2 Xi, vec3 V, float roughness) {
				float alpha = roughness * roughness;

				// Section 4.1: Orthonormal basis
				vec3 T1 = vec3(1.0, 0.0, 0.0);
				vec3 T2 = cross(V, T1);

				// Section 4.2: Parameterization of projected area
				float r = sqrt(Xi.x);
				float phi = 2.0 * PI * Xi.y;
				float t1 = r * cos(phi);
				float t2 = r * sin(phi);
				float s = 0.5 * (1.0 + V.z);
				t2 = (1.0 - s) * sqrt(1.0 - t1 * t1) + s * t2;

				// Section 4.3: Reprojection onto hemisphere
				vec3 Nh = t1 * T1 + t2 * T2 + sqrt(max(0.0, 1.0 - t1 * t1 - t2 * t2)) * V;

				// Section 3.4: Transform back to ellipsoid configuration
				return normalize(vec3(alpha * Nh.x, alpha * Nh.y, max(0.0, Nh.z)));
			}

			void main() {
				vec3 N = normalize(vOutputDirection);
				vec3 V = N; // Assume view direction equals normal for pre-filtering

				vec3 prefilteredColor = vec3(0.0);
				float totalWeight = 0.0;

				// For very low roughness, just sample the environment directly
				if (roughness < 0.001) {
					gl_FragColor = vec4(bilinearCubeUV(envMap, N, mipInt), 1.0);
					return;
				}

				// Tangent space basis for VNDF sampling
				vec3 up = abs(N.z) < 0.999 ? vec3(0.0, 0.0, 1.0) : vec3(1.0, 0.0, 0.0);
				vec3 tangent = normalize(cross(up, N));
				vec3 bitangent = cross(N, tangent);

				for(uint i = 0u; i < uint(GGX_SAMPLES); i++) {
					vec2 Xi = hammersley(i, uint(GGX_SAMPLES));

					// For PMREM, V = N, so in tangent space V is always (0, 0, 1)
					vec3 H_tangent = importanceSampleGGX_VNDF(Xi, vec3(0.0, 0.0, 1.0), roughness);

					// Transform H back to world space
					vec3 H = normalize(tangent * H_tangent.x + bitangent * H_tangent.y + N * H_tangent.z);
					vec3 L = normalize(2.0 * dot(V, H) * H - V);

					float NdotL = max(dot(N, L), 0.0);

					if(NdotL > 0.0) {
						// Sample environment at fixed mip level
						// VNDF importance sampling handles the distribution filtering
						vec3 sampleColor = bilinearCubeUV(envMap, L, mipInt);

						// Weight by NdotL for the split-sum approximation
						// VNDF PDF naturally accounts for the visible microfacet distribution
						prefilteredColor += sampleColor * NdotL;
						totalWeight += NdotL;
					}
				}

				if (totalWeight > 0.0) {
					prefilteredColor = prefilteredColor / totalWeight;
				}

				gl_FragColor = vec4(prefilteredColor, 1.0);
			}
		`,blending:Zn,depthTest:!1,depthWrite:!1})}function hx(i,t,e){const n=new Float32Array(Vi),r=new W(0,1,0);return new Fn({name:"SphericalGaussianBlur",defines:{n:Vi,CUBEUV_TEXEL_WIDTH:1/t,CUBEUV_TEXEL_HEIGHT:1/e,CUBEUV_MAX_MIP:`${i}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:r}},vertexShader:ka(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform int samples;
			uniform float weights[ n ];
			uniform bool latitudinal;
			uniform float dTheta;
			uniform float mipInt;
			uniform vec3 poleAxis;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			vec3 getSample( float theta, vec3 axis ) {

				float cosTheta = cos( theta );
				// Rodrigues' axis-angle rotation
				vec3 sampleDirection = vOutputDirection * cosTheta
					+ cross( axis, vOutputDirection ) * sin( theta )
					+ axis * dot( axis, vOutputDirection ) * ( 1.0 - cosTheta );

				return bilinearCubeUV( envMap, sampleDirection, mipInt );

			}

			void main() {

				vec3 axis = latitudinal ? poleAxis : cross( poleAxis, vOutputDirection );

				if ( all( equal( axis, vec3( 0.0 ) ) ) ) {

					axis = vec3( vOutputDirection.z, 0.0, - vOutputDirection.x );

				}

				axis = normalize( axis );

				gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
				gl_FragColor.rgb += weights[ 0 ] * getSample( 0.0, axis );

				for ( int i = 1; i < n; i++ ) {

					if ( i >= samples ) {

						break;

					}

					float theta = dTheta * float( i );
					gl_FragColor.rgb += weights[ i ] * getSample( -1.0 * theta, axis );
					gl_FragColor.rgb += weights[ i ] * getSample( theta, axis );

				}

			}
		`,blending:Zn,depthTest:!1,depthWrite:!1})}function ku(){return new Fn({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:ka(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;

			#include <common>

			void main() {

				vec3 outputDirection = normalize( vOutputDirection );
				vec2 uv = equirectUv( outputDirection );

				gl_FragColor = vec4( texture2D ( envMap, uv ).rgb, 1.0 );

			}
		`,blending:Zn,depthTest:!1,depthWrite:!1})}function zu(){return new Fn({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:ka(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:Zn,depthTest:!1,depthWrite:!1})}function ka(){return`

		precision mediump float;
		precision mediump int;

		attribute float faceIndex;

		varying vec3 vOutputDirection;

		// RH coordinate system; PMREM face-indexing convention
		vec3 getDirection( vec2 uv, float face ) {

			uv = 2.0 * uv - 1.0;

			vec3 direction = vec3( uv, 1.0 );

			if ( face == 0.0 ) {

				direction = direction.zyx; // ( 1, v, u ) pos x

			} else if ( face == 1.0 ) {

				direction = direction.xzy;
				direction.xz *= -1.0; // ( -u, 1, -v ) pos y

			} else if ( face == 2.0 ) {

				direction.x *= -1.0; // ( -u, v, 1 ) pos z

			} else if ( face == 3.0 ) {

				direction = direction.zyx;
				direction.xz *= -1.0; // ( -1, v, -u ) neg x

			} else if ( face == 4.0 ) {

				direction = direction.xzy;
				direction.xy *= -1.0; // ( -u, -1, v ) neg y

			} else if ( face == 5.0 ) {

				direction.z *= -1.0; // ( u, v, -1 ) neg z

			}

			return direction;

		}

		void main() {

			vOutputDirection = getDirection( uv, faceIndex );
			gl_Position = vec4( position, 1.0 );

		}
	`}class td extends Pn{constructor(t=1,e={}){super(t,t,e),this.isWebGLCubeRenderTarget=!0;const n={width:t,height:t,depth:1},r=[n,n,n,n,n,n];this.texture=new $h(r),this._setTextureOptions(e),this.texture.isRenderTargetTexture=!0}fromEquirectangularTexture(t,e){this.texture.type=e.type,this.texture.colorSpace=e.colorSpace,this.texture.generateMipmaps=e.generateMipmaps,this.texture.minFilter=e.minFilter,this.texture.magFilter=e.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

				varying vec3 vWorldDirection;

				vec3 transformDirection( in vec3 dir, in mat4 matrix ) {

					return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );

				}

				void main() {

					vWorldDirection = transformDirection( position, modelMatrix );

					#include <begin_vertex>
					#include <project_vertex>

				}
			`,fragmentShader:`

				uniform sampler2D tEquirect;

				varying vec3 vWorldDirection;

				#include <common>

				void main() {

					vec3 direction = normalize( vWorldDirection );

					vec2 sampleUV = equirectUv( direction );

					gl_FragColor = texture2D( tEquirect, sampleUV );

				}
			`},r=new Ts(5,5,5),s=new Fn({name:"CubemapFromEquirect",uniforms:Nr(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:We,blending:Zn});s.uniforms.tEquirect.value=e;const a=new Nn(r,s),o=e.minFilter;return e.minFilter===Hi&&(e.minFilter=Ie),new v_(1,10,this).update(t,a),e.minFilter=o,a.geometry.dispose(),a.material.dispose(),this}clear(t,e=!0,n=!0,r=!0){const s=t.getRenderTarget();for(let a=0;a<6;a++)t.setRenderTarget(this,a),t.clear(e,n,r);t.setRenderTarget(s)}}function dx(i){let t=new WeakMap,e=new WeakMap,n=null;function r(f,d=!1){return f==null?null:d?a(f):s(f)}function s(f){if(f&&f.isTexture){const d=f.mapping;if(d===to||d===eo)if(t.has(f)){const _=t.get(f).texture;return o(_,f.mapping)}else{const _=f.image;if(_&&_.height>0){const g=new td(_.height);return g.fromEquirectangularTexture(i,f),t.set(f,g),f.addEventListener("dispose",c),o(g.texture,f.mapping)}else return null}}return f}function a(f){if(f&&f.isTexture){const d=f.mapping,_=d===to||d===eo,g=d===Ji||d===Lr;if(_||g){let p=e.get(f);const m=p!==void 0?p.texture.pmremVersion:0;if(f.isRenderTargetTexture&&f.pmremVersion!==m)return n===null&&(n=new Ou(i)),p=_?n.fromEquirectangular(f,p):n.fromCubemap(f,p),p.texture.pmremVersion=f.pmremVersion,e.set(f,p),p.texture;if(p!==void 0)return p.texture;{const M=f.image;return _&&M&&M.height>0||g&&M&&l(M)?(n===null&&(n=new Ou(i)),p=_?n.fromEquirectangular(f):n.fromCubemap(f),p.texture.pmremVersion=f.pmremVersion,e.set(f,p),f.addEventListener("dispose",u),p.texture):null}}}return f}function o(f,d){return d===to?f.mapping=Ji:d===eo&&(f.mapping=Lr),f}function l(f){let d=0;const _=6;for(let g=0;g<_;g++)f[g]!==void 0&&d++;return d===_}function c(f){const d=f.target;d.removeEventListener("dispose",c);const _=t.get(d);_!==void 0&&(t.delete(d),_.dispose())}function u(f){const d=f.target;d.removeEventListener("dispose",u);const _=e.get(d);_!==void 0&&(e.delete(d),_.dispose())}function h(){t=new WeakMap,e=new WeakMap,n!==null&&(n.dispose(),n=null)}return{get:r,dispose:h}}function px(i){const t={};function e(n){if(t[n]!==void 0)return t[n];const r=i.getExtension(n);return t[n]=r,r}return{has:function(n){return e(n)!==null},init:function(){e("EXT_color_buffer_float"),e("WEBGL_clip_cull_distance"),e("OES_texture_float_linear"),e("EXT_color_buffer_half_float"),e("WEBGL_multisampled_render_to_texture"),e("WEBGL_render_shared_exponent")},get:function(n){const r=e(n);return r===null&&Aa("WebGLRenderer: "+n+" extension not supported."),r}}}function mx(i,t,e,n){const r={},s=new WeakMap;function a(h){const f=h.target;f.index!==null&&t.remove(f.index);for(const _ in f.attributes)t.remove(f.attributes[_]);f.removeEventListener("dispose",a),delete r[f.id];const d=s.get(f);d&&(t.remove(d),s.delete(f)),n.releaseStatesOfGeometry(f),f.isInstancedBufferGeometry===!0&&delete f._maxInstanceCount,e.memory.geometries--}function o(h,f){return r[f.id]===!0||(f.addEventListener("dispose",a),r[f.id]=!0,e.memory.geometries++),f}function l(h){const f=h.attributes;for(const d in f)t.update(f[d],i.ARRAY_BUFFER)}function c(h){const f=[],d=h.index,_=h.attributes.position;let g=0;if(_===void 0)return;if(d!==null){const M=d.array;g=d.version;for(let T=0,S=M.length;T<S;T+=3){const b=M[T+0],A=M[T+1],R=M[T+2];f.push(b,A,A,R,R,b)}}else{const M=_.array;g=_.version;for(let T=0,S=M.length/3-1;T<S;T+=3){const b=T+0,A=T+1,R=T+2;f.push(b,A,A,R,R,b)}}const p=new(_.count>=65535?qh:Xh)(f,1);p.version=g;const m=s.get(h);m&&t.remove(m),s.set(h,p)}function u(h){const f=s.get(h);if(f){const d=h.index;d!==null&&f.version<d.version&&c(h)}else c(h);return s.get(h)}return{get:o,update:l,getWireframeAttribute:u}}function _x(i,t,e){let n;function r(f){n=f}let s,a;function o(f){s=f.type,a=f.bytesPerElement}function l(f,d){i.drawElements(n,d,s,f*a),e.update(d,n,1)}function c(f,d,_){_!==0&&(i.drawElementsInstanced(n,d,s,f*a,_),e.update(d,n,_))}function u(f,d,_){if(_===0)return;t.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,d,0,s,f,0,_);let p=0;for(let m=0;m<_;m++)p+=d[m];e.update(p,n,1)}function h(f,d,_,g){if(_===0)return;const p=t.get("WEBGL_multi_draw");if(p===null)for(let m=0;m<f.length;m++)c(f[m]/a,d[m],g[m]);else{p.multiDrawElementsInstancedWEBGL(n,d,0,s,f,0,g,0,_);let m=0;for(let M=0;M<_;M++)m+=d[M]*g[M];e.update(m,n,1)}}this.setMode=r,this.setIndex=o,this.render=l,this.renderInstances=c,this.renderMultiDraw=u,this.renderMultiDrawInstances=h}function gx(i){const t={geometries:0,textures:0},e={frame:0,calls:0,triangles:0,points:0,lines:0};function n(s,a,o){switch(e.calls++,a){case i.TRIANGLES:e.triangles+=o*(s/3);break;case i.LINES:e.lines+=o*(s/2);break;case i.LINE_STRIP:e.lines+=o*(s-1);break;case i.LINE_LOOP:e.lines+=o*s;break;case i.POINTS:e.points+=o*s;break;default:Xt("WebGLInfo: Unknown draw mode:",a);break}}function r(){e.calls=0,e.triangles=0,e.points=0,e.lines=0}return{memory:t,render:e,programs:null,autoReset:!0,reset:r,update:n}}function xx(i,t,e){const n=new WeakMap,r=new me;function s(a,o,l){const c=a.morphTargetInfluences,u=o.morphAttributes.position||o.morphAttributes.normal||o.morphAttributes.color,h=u!==void 0?u.length:0;let f=n.get(o);if(f===void 0||f.count!==h){let G=function(){x.dispose(),n.delete(o),o.removeEventListener("dispose",G)};var d=G;f!==void 0&&f.texture.dispose();const _=o.morphAttributes.position!==void 0,g=o.morphAttributes.normal!==void 0,p=o.morphAttributes.color!==void 0,m=o.morphAttributes.position||[],M=o.morphAttributes.normal||[],T=o.morphAttributes.color||[];let S=0;_===!0&&(S=1),g===!0&&(S=2),p===!0&&(S=3);let b=o.attributes.position.count*S,A=1;b>t.maxTextureSize&&(A=Math.ceil(b/t.maxTextureSize),b=t.maxTextureSize);const R=new Float32Array(b*A*4*h),x=new Gh(R,b,A,h);x.type=wn,x.needsUpdate=!0;const y=S*4;for(let D=0;D<h;D++){const B=m[D],k=M[D],X=T[D],C=b*A*4*D;for(let L=0;L<B.count;L++){const P=L*y;_===!0&&(r.fromBufferAttribute(B,L),R[C+P+0]=r.x,R[C+P+1]=r.y,R[C+P+2]=r.z,R[C+P+3]=0),g===!0&&(r.fromBufferAttribute(k,L),R[C+P+4]=r.x,R[C+P+5]=r.y,R[C+P+6]=r.z,R[C+P+7]=0),p===!0&&(r.fromBufferAttribute(X,L),R[C+P+8]=r.x,R[C+P+9]=r.y,R[C+P+10]=r.z,R[C+P+11]=X.itemSize===4?r.w:1)}}f={count:h,texture:x,size:new Qt(b,A)},n.set(o,f),o.addEventListener("dispose",G)}if(a.isInstancedMesh===!0&&a.morphTexture!==null)l.getUniforms().setValue(i,"morphTexture",a.morphTexture,e);else{let _=0;for(let p=0;p<c.length;p++)_+=c[p];const g=o.morphTargetsRelative?1:1-_;l.getUniforms().setValue(i,"morphTargetBaseInfluence",g),l.getUniforms().setValue(i,"morphTargetInfluences",c)}l.getUniforms().setValue(i,"morphTargetsTexture",f.texture,e),l.getUniforms().setValue(i,"morphTargetsTextureSize",f.size)}return{update:s}}function vx(i,t,e,n,r){let s=new WeakMap;function a(c){const u=r.render.frame,h=c.geometry,f=t.get(c,h);if(s.get(f)!==u&&(t.update(f),s.set(f,u)),c.isInstancedMesh&&(c.hasEventListener("dispose",l)===!1&&c.addEventListener("dispose",l),s.get(c)!==u&&(e.update(c.instanceMatrix,i.ARRAY_BUFFER),c.instanceColor!==null&&e.update(c.instanceColor,i.ARRAY_BUFFER),s.set(c,u))),c.isSkinnedMesh){const d=c.skeleton;s.get(d)!==u&&(d.update(),s.set(d,u))}return f}function o(){s=new WeakMap}function l(c){const u=c.target;u.removeEventListener("dispose",l),n.releaseStatesOfObject(u),e.remove(u.instanceMatrix),u.instanceColor!==null&&e.remove(u.instanceColor)}return{update:a,dispose:o}}const Mx={[Ah]:"LINEAR_TONE_MAPPING",[wh]:"REINHARD_TONE_MAPPING",[Rh]:"CINEON_TONE_MAPPING",[Ch]:"ACES_FILMIC_TONE_MAPPING",[Dh]:"AGX_TONE_MAPPING",[Lh]:"NEUTRAL_TONE_MAPPING",[Ph]:"CUSTOM_TONE_MAPPING"};function Sx(i,t,e,n,r){const s=new Pn(t,e,{type:i,depthBuffer:n,stencilBuffer:r}),a=new Pn(t,e,{type:ei,depthBuffer:!1,stencilBuffer:!1}),o=new si;o.setAttribute("position",new jn([-1,3,0,-1,-1,0,3,-1,0],3)),o.setAttribute("uv",new jn([0,2,0,0,2,0],2));const l=new __({uniforms:{tDiffuse:{value:null}},vertexShader:`
			precision highp float;

			uniform mat4 modelViewMatrix;
			uniform mat4 projectionMatrix;

			attribute vec3 position;
			attribute vec2 uv;

			varying vec2 vUv;

			void main() {
				vUv = uv;
				gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
			}`,fragmentShader:`
			precision highp float;

			uniform sampler2D tDiffuse;

			varying vec2 vUv;

			#include <tonemapping_pars_fragment>
			#include <colorspace_pars_fragment>

			void main() {
				gl_FragColor = texture2D( tDiffuse, vUv );

				#ifdef LINEAR_TONE_MAPPING
					gl_FragColor.rgb = LinearToneMapping( gl_FragColor.rgb );
				#elif defined( REINHARD_TONE_MAPPING )
					gl_FragColor.rgb = ReinhardToneMapping( gl_FragColor.rgb );
				#elif defined( CINEON_TONE_MAPPING )
					gl_FragColor.rgb = CineonToneMapping( gl_FragColor.rgb );
				#elif defined( ACES_FILMIC_TONE_MAPPING )
					gl_FragColor.rgb = ACESFilmicToneMapping( gl_FragColor.rgb );
				#elif defined( AGX_TONE_MAPPING )
					gl_FragColor.rgb = AgXToneMapping( gl_FragColor.rgb );
				#elif defined( NEUTRAL_TONE_MAPPING )
					gl_FragColor.rgb = NeutralToneMapping( gl_FragColor.rgb );
				#elif defined( CUSTOM_TONE_MAPPING )
					gl_FragColor.rgb = CustomToneMapping( gl_FragColor.rgb );
				#endif

				#ifdef SRGB_TRANSFER
					gl_FragColor = sRGBTransferOETF( gl_FragColor );
				#endif
			}`,depthTest:!1,depthWrite:!1}),c=new Nn(o,l),u=new jh(-1,1,1,-1,0,1);let h=null,f=null,d=!1,_,g=null,p=[],m=!1;this.setSize=function(M,T){s.setSize(M,T),a.setSize(M,T);for(let S=0;S<p.length;S++){const b=p[S];b.setSize&&b.setSize(M,T)}},this.setEffects=function(M){p=M,m=p.length>0&&p[0].isRenderPass===!0;const T=s.width,S=s.height;for(let b=0;b<p.length;b++){const A=p[b];A.setSize&&A.setSize(T,S)}},this.begin=function(M,T){if(d||M.toneMapping===Cn&&p.length===0)return!1;if(g=T,T!==null){const S=T.width,b=T.height;(s.width!==S||s.height!==b)&&this.setSize(S,b)}return m===!1&&M.setRenderTarget(s),_=M.toneMapping,M.toneMapping=Cn,!0},this.hasRenderPass=function(){return m},this.end=function(M,T){M.toneMapping=_,d=!0;let S=s,b=a;for(let A=0;A<p.length;A++){const R=p[A];if(R.enabled!==!1&&(R.render(M,b,S,T),R.needsSwap!==!1)){const x=S;S=b,b=x}}if(h!==M.outputColorSpace||f!==M.toneMapping){h=M.outputColorSpace,f=M.toneMapping,l.defines={},Ht.getTransfer(h)===Kt&&(l.defines.SRGB_TRANSFER="");const A=Mx[f];A&&(l.defines[A]=""),l.needsUpdate=!0}l.uniforms.tDiffuse.value=S.texture,M.setRenderTarget(g),M.render(c,u),g=null,d=!1},this.isCompositing=function(){return d},this.dispose=function(){s.dispose(),a.dispose(),o.dispose(),l.dispose()}}const ed=new Oe,Gl=new _s(1,1),nd=new Gh,id=new qm,rd=new $h,Vu=[],Gu=[],Hu=new Float32Array(16),Wu=new Float32Array(9),Xu=new Float32Array(4);function zr(i,t,e){const n=i[0];if(n<=0||n>0)return i;const r=t*e;let s=Vu[r];if(s===void 0&&(s=new Float32Array(r),Vu[r]=s),t!==0){n.toArray(s,0);for(let a=1,o=0;a!==t;++a)o+=e,i[a].toArray(s,o)}return s}function Me(i,t){if(i.length!==t.length)return!1;for(let e=0,n=i.length;e<n;e++)if(i[e]!==t[e])return!1;return!0}function Se(i,t){for(let e=0,n=t.length;e<n;e++)i[e]=t[e]}function za(i,t){let e=Gu[t];e===void 0&&(e=new Int32Array(t),Gu[t]=e);for(let n=0;n!==t;++n)e[n]=i.allocateTextureUnit();return e}function yx(i,t){const e=this.cache;e[0]!==t&&(i.uniform1f(this.addr,t),e[0]=t)}function Ex(i,t){const e=this.cache;if(t.x!==void 0)(e[0]!==t.x||e[1]!==t.y)&&(i.uniform2f(this.addr,t.x,t.y),e[0]=t.x,e[1]=t.y);else{if(Me(e,t))return;i.uniform2fv(this.addr,t),Se(e,t)}}function Tx(i,t){const e=this.cache;if(t.x!==void 0)(e[0]!==t.x||e[1]!==t.y||e[2]!==t.z)&&(i.uniform3f(this.addr,t.x,t.y,t.z),e[0]=t.x,e[1]=t.y,e[2]=t.z);else if(t.r!==void 0)(e[0]!==t.r||e[1]!==t.g||e[2]!==t.b)&&(i.uniform3f(this.addr,t.r,t.g,t.b),e[0]=t.r,e[1]=t.g,e[2]=t.b);else{if(Me(e,t))return;i.uniform3fv(this.addr,t),Se(e,t)}}function bx(i,t){const e=this.cache;if(t.x!==void 0)(e[0]!==t.x||e[1]!==t.y||e[2]!==t.z||e[3]!==t.w)&&(i.uniform4f(this.addr,t.x,t.y,t.z,t.w),e[0]=t.x,e[1]=t.y,e[2]=t.z,e[3]=t.w);else{if(Me(e,t))return;i.uniform4fv(this.addr,t),Se(e,t)}}function Ax(i,t){const e=this.cache,n=t.elements;if(n===void 0){if(Me(e,t))return;i.uniformMatrix2fv(this.addr,!1,t),Se(e,t)}else{if(Me(e,n))return;Xu.set(n),i.uniformMatrix2fv(this.addr,!1,Xu),Se(e,n)}}function wx(i,t){const e=this.cache,n=t.elements;if(n===void 0){if(Me(e,t))return;i.uniformMatrix3fv(this.addr,!1,t),Se(e,t)}else{if(Me(e,n))return;Wu.set(n),i.uniformMatrix3fv(this.addr,!1,Wu),Se(e,n)}}function Rx(i,t){const e=this.cache,n=t.elements;if(n===void 0){if(Me(e,t))return;i.uniformMatrix4fv(this.addr,!1,t),Se(e,t)}else{if(Me(e,n))return;Hu.set(n),i.uniformMatrix4fv(this.addr,!1,Hu),Se(e,n)}}function Cx(i,t){const e=this.cache;e[0]!==t&&(i.uniform1i(this.addr,t),e[0]=t)}function Px(i,t){const e=this.cache;if(t.x!==void 0)(e[0]!==t.x||e[1]!==t.y)&&(i.uniform2i(this.addr,t.x,t.y),e[0]=t.x,e[1]=t.y);else{if(Me(e,t))return;i.uniform2iv(this.addr,t),Se(e,t)}}function Dx(i,t){const e=this.cache;if(t.x!==void 0)(e[0]!==t.x||e[1]!==t.y||e[2]!==t.z)&&(i.uniform3i(this.addr,t.x,t.y,t.z),e[0]=t.x,e[1]=t.y,e[2]=t.z);else{if(Me(e,t))return;i.uniform3iv(this.addr,t),Se(e,t)}}function Lx(i,t){const e=this.cache;if(t.x!==void 0)(e[0]!==t.x||e[1]!==t.y||e[2]!==t.z||e[3]!==t.w)&&(i.uniform4i(this.addr,t.x,t.y,t.z,t.w),e[0]=t.x,e[1]=t.y,e[2]=t.z,e[3]=t.w);else{if(Me(e,t))return;i.uniform4iv(this.addr,t),Se(e,t)}}function Ix(i,t){const e=this.cache;e[0]!==t&&(i.uniform1ui(this.addr,t),e[0]=t)}function Ux(i,t){const e=this.cache;if(t.x!==void 0)(e[0]!==t.x||e[1]!==t.y)&&(i.uniform2ui(this.addr,t.x,t.y),e[0]=t.x,e[1]=t.y);else{if(Me(e,t))return;i.uniform2uiv(this.addr,t),Se(e,t)}}function Nx(i,t){const e=this.cache;if(t.x!==void 0)(e[0]!==t.x||e[1]!==t.y||e[2]!==t.z)&&(i.uniform3ui(this.addr,t.x,t.y,t.z),e[0]=t.x,e[1]=t.y,e[2]=t.z);else{if(Me(e,t))return;i.uniform3uiv(this.addr,t),Se(e,t)}}function Fx(i,t){const e=this.cache;if(t.x!==void 0)(e[0]!==t.x||e[1]!==t.y||e[2]!==t.z||e[3]!==t.w)&&(i.uniform4ui(this.addr,t.x,t.y,t.z,t.w),e[0]=t.x,e[1]=t.y,e[2]=t.z,e[3]=t.w);else{if(Me(e,t))return;i.uniform4uiv(this.addr,t),Se(e,t)}}function Ox(i,t,e){const n=this.cache,r=e.allocateTextureUnit();n[0]!==r&&(i.uniform1i(this.addr,r),n[0]=r);let s;this.type===i.SAMPLER_2D_SHADOW?(Gl.compareFunction=e.isReversedDepthBuffer()?Ac:bc,s=Gl):s=ed,e.setTexture2D(t||s,r)}function Bx(i,t,e){const n=this.cache,r=e.allocateTextureUnit();n[0]!==r&&(i.uniform1i(this.addr,r),n[0]=r),e.setTexture3D(t||id,r)}function kx(i,t,e){const n=this.cache,r=e.allocateTextureUnit();n[0]!==r&&(i.uniform1i(this.addr,r),n[0]=r),e.setTextureCube(t||rd,r)}function zx(i,t,e){const n=this.cache,r=e.allocateTextureUnit();n[0]!==r&&(i.uniform1i(this.addr,r),n[0]=r),e.setTexture2DArray(t||nd,r)}function Vx(i){switch(i){case 5126:return yx;case 35664:return Ex;case 35665:return Tx;case 35666:return bx;case 35674:return Ax;case 35675:return wx;case 35676:return Rx;case 5124:case 35670:return Cx;case 35667:case 35671:return Px;case 35668:case 35672:return Dx;case 35669:case 35673:return Lx;case 5125:return Ix;case 36294:return Ux;case 36295:return Nx;case 36296:return Fx;case 35678:case 36198:case 36298:case 36306:case 35682:return Ox;case 35679:case 36299:case 36307:return Bx;case 35680:case 36300:case 36308:case 36293:return kx;case 36289:case 36303:case 36311:case 36292:return zx}}function Gx(i,t){i.uniform1fv(this.addr,t)}function Hx(i,t){const e=zr(t,this.size,2);i.uniform2fv(this.addr,e)}function Wx(i,t){const e=zr(t,this.size,3);i.uniform3fv(this.addr,e)}function Xx(i,t){const e=zr(t,this.size,4);i.uniform4fv(this.addr,e)}function qx(i,t){const e=zr(t,this.size,4);i.uniformMatrix2fv(this.addr,!1,e)}function Yx(i,t){const e=zr(t,this.size,9);i.uniformMatrix3fv(this.addr,!1,e)}function $x(i,t){const e=zr(t,this.size,16);i.uniformMatrix4fv(this.addr,!1,e)}function Kx(i,t){i.uniform1iv(this.addr,t)}function Zx(i,t){i.uniform2iv(this.addr,t)}function Jx(i,t){i.uniform3iv(this.addr,t)}function jx(i,t){i.uniform4iv(this.addr,t)}function Qx(i,t){i.uniform1uiv(this.addr,t)}function tv(i,t){i.uniform2uiv(this.addr,t)}function ev(i,t){i.uniform3uiv(this.addr,t)}function nv(i,t){i.uniform4uiv(this.addr,t)}function iv(i,t,e){const n=this.cache,r=t.length,s=za(e,r);Me(n,s)||(i.uniform1iv(this.addr,s),Se(n,s));let a;this.type===i.SAMPLER_2D_SHADOW?a=Gl:a=ed;for(let o=0;o!==r;++o)e.setTexture2D(t[o]||a,s[o])}function rv(i,t,e){const n=this.cache,r=t.length,s=za(e,r);Me(n,s)||(i.uniform1iv(this.addr,s),Se(n,s));for(let a=0;a!==r;++a)e.setTexture3D(t[a]||id,s[a])}function sv(i,t,e){const n=this.cache,r=t.length,s=za(e,r);Me(n,s)||(i.uniform1iv(this.addr,s),Se(n,s));for(let a=0;a!==r;++a)e.setTextureCube(t[a]||rd,s[a])}function av(i,t,e){const n=this.cache,r=t.length,s=za(e,r);Me(n,s)||(i.uniform1iv(this.addr,s),Se(n,s));for(let a=0;a!==r;++a)e.setTexture2DArray(t[a]||nd,s[a])}function ov(i){switch(i){case 5126:return Gx;case 35664:return Hx;case 35665:return Wx;case 35666:return Xx;case 35674:return qx;case 35675:return Yx;case 35676:return $x;case 5124:case 35670:return Kx;case 35667:case 35671:return Zx;case 35668:case 35672:return Jx;case 35669:case 35673:return jx;case 5125:return Qx;case 36294:return tv;case 36295:return ev;case 36296:return nv;case 35678:case 36198:case 36298:case 36306:case 35682:return iv;case 35679:case 36299:case 36307:return rv;case 35680:case 36300:case 36308:case 36293:return sv;case 36289:case 36303:case 36311:case 36292:return av}}class lv{constructor(t,e,n){this.id=t,this.addr=n,this.cache=[],this.type=e.type,this.setValue=Vx(e.type)}}class cv{constructor(t,e,n){this.id=t,this.addr=n,this.cache=[],this.type=e.type,this.size=e.size,this.setValue=ov(e.type)}}class uv{constructor(t){this.id=t,this.seq=[],this.map={}}setValue(t,e,n){const r=this.seq;for(let s=0,a=r.length;s!==a;++s){const o=r[s];o.setValue(t,e[o.id],n)}}}const Lo=/(\w+)(\])?(\[|\.)?/g;function qu(i,t){i.seq.push(t),i.map[t.id]=t}function fv(i,t,e){const n=i.name,r=n.length;for(Lo.lastIndex=0;;){const s=Lo.exec(n),a=Lo.lastIndex;let o=s[1];const l=s[2]==="]",c=s[3];if(l&&(o=o|0),c===void 0||c==="["&&a+2===r){qu(e,c===void 0?new lv(o,i,t):new cv(o,i,t));break}else{let h=e.map[o];h===void 0&&(h=new uv(o),qu(e,h)),e=h}}}class ha{constructor(t,e){this.seq=[],this.map={};const n=t.getProgramParameter(e,t.ACTIVE_UNIFORMS);for(let a=0;a<n;++a){const o=t.getActiveUniform(e,a),l=t.getUniformLocation(e,o.name);fv(o,l,this)}const r=[],s=[];for(const a of this.seq)a.type===t.SAMPLER_2D_SHADOW||a.type===t.SAMPLER_CUBE_SHADOW||a.type===t.SAMPLER_2D_ARRAY_SHADOW?r.push(a):s.push(a);r.length>0&&(this.seq=r.concat(s))}setValue(t,e,n,r){const s=this.map[e];s!==void 0&&s.setValue(t,n,r)}setOptional(t,e,n){const r=e[n];r!==void 0&&this.setValue(t,n,r)}static upload(t,e,n,r){for(let s=0,a=e.length;s!==a;++s){const o=e[s],l=n[o.id];l.needsUpdate!==!1&&o.setValue(t,l.value,r)}}static seqWithValue(t,e){const n=[];for(let r=0,s=t.length;r!==s;++r){const a=t[r];a.id in e&&n.push(a)}return n}}function Yu(i,t,e){const n=i.createShader(t);return i.shaderSource(n,e),i.compileShader(n),n}const hv=37297;let dv=0;function pv(i,t){const e=i.split(`
`),n=[],r=Math.max(t-6,0),s=Math.min(t+6,e.length);for(let a=r;a<s;a++){const o=a+1;n.push(`${o===t?">":" "} ${o}: ${e[a]}`)}return n.join(`
`)}const $u=new It;function mv(i){Ht._getMatrix($u,Ht.workingColorSpace,i);const t=`mat3( ${$u.elements.map(e=>e.toFixed(4))} )`;switch(Ht.getTransfer(i)){case Ea:return[t,"LinearTransferOETF"];case Kt:return[t,"sRGBTransferOETF"];default:return Pt("WebGLProgram: Unsupported color space: ",i),[t,"LinearTransferOETF"]}}function Ku(i,t,e){const n=i.getShaderParameter(t,i.COMPILE_STATUS),s=(i.getShaderInfoLog(t)||"").trim();if(n&&s==="")return"";const a=/ERROR: 0:(\d+)/.exec(s);if(a){const o=parseInt(a[1]);return e.toUpperCase()+`

`+s+`

`+pv(i.getShaderSource(t),o)}else return s}function _v(i,t){const e=mv(t);return[`vec4 ${i}( vec4 value ) {`,`	return ${e[1]}( vec4( value.rgb * ${e[0]}, value.a ) );`,"}"].join(`
`)}const gv={[Ah]:"Linear",[wh]:"Reinhard",[Rh]:"Cineon",[Ch]:"ACESFilmic",[Dh]:"AgX",[Lh]:"Neutral",[Ph]:"Custom"};function xv(i,t){const e=gv[t];return e===void 0?(Pt("WebGLProgram: Unsupported toneMapping:",t),"vec3 "+i+"( vec3 color ) { return LinearToneMapping( color ); }"):"vec3 "+i+"( vec3 color ) { return "+e+"ToneMapping( color ); }"}const Qs=new W;function vv(){Ht.getLuminanceCoefficients(Qs);const i=Qs.x.toFixed(4),t=Qs.y.toFixed(4),e=Qs.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${i}, ${t}, ${e} );`,"	return dot( weights, rgb );","}"].join(`
`)}function Mv(i){return[i.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",i.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(Qr).join(`
`)}function Sv(i){const t=[];for(const e in i){const n=i[e];n!==!1&&t.push("#define "+e+" "+n)}return t.join(`
`)}function yv(i,t){const e={},n=i.getProgramParameter(t,i.ACTIVE_ATTRIBUTES);for(let r=0;r<n;r++){const s=i.getActiveAttrib(t,r),a=s.name;let o=1;s.type===i.FLOAT_MAT2&&(o=2),s.type===i.FLOAT_MAT3&&(o=3),s.type===i.FLOAT_MAT4&&(o=4),e[a]={type:s.type,location:i.getAttribLocation(t,a),locationSize:o}}return e}function Qr(i){return i!==""}function Zu(i,t){const e=t.numSpotLightShadows+t.numSpotLightMaps-t.numSpotLightShadowsWithMaps;return i.replace(/NUM_DIR_LIGHTS/g,t.numDirLights).replace(/NUM_SPOT_LIGHTS/g,t.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,t.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,e).replace(/NUM_RECT_AREA_LIGHTS/g,t.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,t.numPointLights).replace(/NUM_HEMI_LIGHTS/g,t.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,t.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,t.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,t.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,t.numPointLightShadows)}function Ju(i,t){return i.replace(/NUM_CLIPPING_PLANES/g,t.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,t.numClippingPlanes-t.numClipIntersection)}const Ev=/^[ \t]*#include +<([\w\d./]+)>/gm;function Hl(i){return i.replace(Ev,bv)}const Tv=new Map;function bv(i,t){let e=Nt[t];if(e===void 0){const n=Tv.get(t);if(n!==void 0)e=Nt[n],Pt('WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',t,n);else throw new Error("Can not resolve #include <"+t+">")}return Hl(e)}const Av=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function ju(i){return i.replace(Av,wv)}function wv(i,t,e,n){let r="";for(let s=parseInt(t);s<parseInt(e);s++)r+=n.replace(/\[\s*i\s*\]/g,"[ "+s+" ]").replace(/UNROLLED_LOOP_INDEX/g,s);return r}function Qu(i){let t=`precision ${i.precision} float;
	precision ${i.precision} int;
	precision ${i.precision} sampler2D;
	precision ${i.precision} samplerCube;
	precision ${i.precision} sampler3D;
	precision ${i.precision} sampler2DArray;
	precision ${i.precision} sampler2DShadow;
	precision ${i.precision} samplerCubeShadow;
	precision ${i.precision} sampler2DArrayShadow;
	precision ${i.precision} isampler2D;
	precision ${i.precision} isampler3D;
	precision ${i.precision} isamplerCube;
	precision ${i.precision} isampler2DArray;
	precision ${i.precision} usampler2D;
	precision ${i.precision} usampler3D;
	precision ${i.precision} usamplerCube;
	precision ${i.precision} usampler2DArray;
	`;return i.precision==="highp"?t+=`
#define HIGH_PRECISION`:i.precision==="mediump"?t+=`
#define MEDIUM_PRECISION`:i.precision==="lowp"&&(t+=`
#define LOW_PRECISION`),t}const Rv={[oa]:"SHADOWMAP_TYPE_PCF",[jr]:"SHADOWMAP_TYPE_VSM"};function Cv(i){return Rv[i.shadowMapType]||"SHADOWMAP_TYPE_BASIC"}const Pv={[Ji]:"ENVMAP_TYPE_CUBE",[Lr]:"ENVMAP_TYPE_CUBE",[Oa]:"ENVMAP_TYPE_CUBE_UV"};function Dv(i){return i.envMap===!1?"ENVMAP_TYPE_CUBE":Pv[i.envMapMode]||"ENVMAP_TYPE_CUBE"}const Lv={[Lr]:"ENVMAP_MODE_REFRACTION"};function Iv(i){return i.envMap===!1?"ENVMAP_MODE_REFLECTION":Lv[i.envMapMode]||"ENVMAP_MODE_REFLECTION"}const Uv={[bh]:"ENVMAP_BLENDING_MULTIPLY",[Tm]:"ENVMAP_BLENDING_MIX",[bm]:"ENVMAP_BLENDING_ADD"};function Nv(i){return i.envMap===!1?"ENVMAP_BLENDING_NONE":Uv[i.combine]||"ENVMAP_BLENDING_NONE"}function Fv(i){const t=i.envMapCubeUVHeight;if(t===null)return null;const e=Math.log2(t)-2,n=1/t;return{texelWidth:1/(3*Math.max(Math.pow(2,e),7*16)),texelHeight:n,maxMip:e}}function Ov(i,t,e,n){const r=i.getContext(),s=e.defines;let a=e.vertexShader,o=e.fragmentShader;const l=Cv(e),c=Dv(e),u=Iv(e),h=Nv(e),f=Fv(e),d=Mv(e),_=Sv(s),g=r.createProgram();let p,m,M=e.glslVersion?"#version "+e.glslVersion+`
`:"";e.isRawShaderMaterial?(p=["#define SHADER_TYPE "+e.shaderType,"#define SHADER_NAME "+e.shaderName,_].filter(Qr).join(`
`),p.length>0&&(p+=`
`),m=["#define SHADER_TYPE "+e.shaderType,"#define SHADER_NAME "+e.shaderName,_].filter(Qr).join(`
`),m.length>0&&(m+=`
`)):(p=[Qu(e),"#define SHADER_TYPE "+e.shaderType,"#define SHADER_NAME "+e.shaderName,_,e.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",e.batching?"#define USE_BATCHING":"",e.batchingColor?"#define USE_BATCHING_COLOR":"",e.instancing?"#define USE_INSTANCING":"",e.instancingColor?"#define USE_INSTANCING_COLOR":"",e.instancingMorph?"#define USE_INSTANCING_MORPH":"",e.useFog&&e.fog?"#define USE_FOG":"",e.useFog&&e.fogExp2?"#define FOG_EXP2":"",e.map?"#define USE_MAP":"",e.envMap?"#define USE_ENVMAP":"",e.envMap?"#define "+u:"",e.lightMap?"#define USE_LIGHTMAP":"",e.aoMap?"#define USE_AOMAP":"",e.bumpMap?"#define USE_BUMPMAP":"",e.normalMap?"#define USE_NORMALMAP":"",e.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",e.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",e.displacementMap?"#define USE_DISPLACEMENTMAP":"",e.emissiveMap?"#define USE_EMISSIVEMAP":"",e.anisotropy?"#define USE_ANISOTROPY":"",e.anisotropyMap?"#define USE_ANISOTROPYMAP":"",e.clearcoatMap?"#define USE_CLEARCOATMAP":"",e.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",e.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",e.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",e.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",e.specularMap?"#define USE_SPECULARMAP":"",e.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",e.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",e.roughnessMap?"#define USE_ROUGHNESSMAP":"",e.metalnessMap?"#define USE_METALNESSMAP":"",e.alphaMap?"#define USE_ALPHAMAP":"",e.alphaHash?"#define USE_ALPHAHASH":"",e.transmission?"#define USE_TRANSMISSION":"",e.transmissionMap?"#define USE_TRANSMISSIONMAP":"",e.thicknessMap?"#define USE_THICKNESSMAP":"",e.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",e.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",e.mapUv?"#define MAP_UV "+e.mapUv:"",e.alphaMapUv?"#define ALPHAMAP_UV "+e.alphaMapUv:"",e.lightMapUv?"#define LIGHTMAP_UV "+e.lightMapUv:"",e.aoMapUv?"#define AOMAP_UV "+e.aoMapUv:"",e.emissiveMapUv?"#define EMISSIVEMAP_UV "+e.emissiveMapUv:"",e.bumpMapUv?"#define BUMPMAP_UV "+e.bumpMapUv:"",e.normalMapUv?"#define NORMALMAP_UV "+e.normalMapUv:"",e.displacementMapUv?"#define DISPLACEMENTMAP_UV "+e.displacementMapUv:"",e.metalnessMapUv?"#define METALNESSMAP_UV "+e.metalnessMapUv:"",e.roughnessMapUv?"#define ROUGHNESSMAP_UV "+e.roughnessMapUv:"",e.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+e.anisotropyMapUv:"",e.clearcoatMapUv?"#define CLEARCOATMAP_UV "+e.clearcoatMapUv:"",e.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+e.clearcoatNormalMapUv:"",e.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+e.clearcoatRoughnessMapUv:"",e.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+e.iridescenceMapUv:"",e.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+e.iridescenceThicknessMapUv:"",e.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+e.sheenColorMapUv:"",e.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+e.sheenRoughnessMapUv:"",e.specularMapUv?"#define SPECULARMAP_UV "+e.specularMapUv:"",e.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+e.specularColorMapUv:"",e.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+e.specularIntensityMapUv:"",e.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+e.transmissionMapUv:"",e.thicknessMapUv?"#define THICKNESSMAP_UV "+e.thicknessMapUv:"",e.vertexTangents&&e.flatShading===!1?"#define USE_TANGENT":"",e.vertexColors?"#define USE_COLOR":"",e.vertexAlphas?"#define USE_COLOR_ALPHA":"",e.vertexUv1s?"#define USE_UV1":"",e.vertexUv2s?"#define USE_UV2":"",e.vertexUv3s?"#define USE_UV3":"",e.pointsUvs?"#define USE_POINTS_UV":"",e.flatShading?"#define FLAT_SHADED":"",e.skinning?"#define USE_SKINNING":"",e.morphTargets?"#define USE_MORPHTARGETS":"",e.morphNormals&&e.flatShading===!1?"#define USE_MORPHNORMALS":"",e.morphColors?"#define USE_MORPHCOLORS":"",e.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+e.morphTextureStride:"",e.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+e.morphTargetsCount:"",e.doubleSided?"#define DOUBLE_SIDED":"",e.flipSided?"#define FLIP_SIDED":"",e.shadowMapEnabled?"#define USE_SHADOWMAP":"",e.shadowMapEnabled?"#define "+l:"",e.sizeAttenuation?"#define USE_SIZEATTENUATION":"",e.numLightProbes>0?"#define USE_LIGHT_PROBES":"",e.logarithmicDepthBuffer?"#define USE_LOGARITHMIC_DEPTH_BUFFER":"",e.reversedDepthBuffer?"#define USE_REVERSED_DEPTH_BUFFER":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(Qr).join(`
`),m=[Qu(e),"#define SHADER_TYPE "+e.shaderType,"#define SHADER_NAME "+e.shaderName,_,e.useFog&&e.fog?"#define USE_FOG":"",e.useFog&&e.fogExp2?"#define FOG_EXP2":"",e.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",e.map?"#define USE_MAP":"",e.matcap?"#define USE_MATCAP":"",e.envMap?"#define USE_ENVMAP":"",e.envMap?"#define "+c:"",e.envMap?"#define "+u:"",e.envMap?"#define "+h:"",f?"#define CUBEUV_TEXEL_WIDTH "+f.texelWidth:"",f?"#define CUBEUV_TEXEL_HEIGHT "+f.texelHeight:"",f?"#define CUBEUV_MAX_MIP "+f.maxMip+".0":"",e.lightMap?"#define USE_LIGHTMAP":"",e.aoMap?"#define USE_AOMAP":"",e.bumpMap?"#define USE_BUMPMAP":"",e.normalMap?"#define USE_NORMALMAP":"",e.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",e.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",e.emissiveMap?"#define USE_EMISSIVEMAP":"",e.anisotropy?"#define USE_ANISOTROPY":"",e.anisotropyMap?"#define USE_ANISOTROPYMAP":"",e.clearcoat?"#define USE_CLEARCOAT":"",e.clearcoatMap?"#define USE_CLEARCOATMAP":"",e.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",e.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",e.dispersion?"#define USE_DISPERSION":"",e.iridescence?"#define USE_IRIDESCENCE":"",e.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",e.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",e.specularMap?"#define USE_SPECULARMAP":"",e.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",e.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",e.roughnessMap?"#define USE_ROUGHNESSMAP":"",e.metalnessMap?"#define USE_METALNESSMAP":"",e.alphaMap?"#define USE_ALPHAMAP":"",e.alphaTest?"#define USE_ALPHATEST":"",e.alphaHash?"#define USE_ALPHAHASH":"",e.sheen?"#define USE_SHEEN":"",e.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",e.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",e.transmission?"#define USE_TRANSMISSION":"",e.transmissionMap?"#define USE_TRANSMISSIONMAP":"",e.thicknessMap?"#define USE_THICKNESSMAP":"",e.vertexTangents&&e.flatShading===!1?"#define USE_TANGENT":"",e.vertexColors||e.instancingColor?"#define USE_COLOR":"",e.vertexAlphas||e.batchingColor?"#define USE_COLOR_ALPHA":"",e.vertexUv1s?"#define USE_UV1":"",e.vertexUv2s?"#define USE_UV2":"",e.vertexUv3s?"#define USE_UV3":"",e.pointsUvs?"#define USE_POINTS_UV":"",e.gradientMap?"#define USE_GRADIENTMAP":"",e.flatShading?"#define FLAT_SHADED":"",e.doubleSided?"#define DOUBLE_SIDED":"",e.flipSided?"#define FLIP_SIDED":"",e.shadowMapEnabled?"#define USE_SHADOWMAP":"",e.shadowMapEnabled?"#define "+l:"",e.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",e.numLightProbes>0?"#define USE_LIGHT_PROBES":"",e.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",e.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",e.logarithmicDepthBuffer?"#define USE_LOGARITHMIC_DEPTH_BUFFER":"",e.reversedDepthBuffer?"#define USE_REVERSED_DEPTH_BUFFER":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",e.toneMapping!==Cn?"#define TONE_MAPPING":"",e.toneMapping!==Cn?Nt.tonemapping_pars_fragment:"",e.toneMapping!==Cn?xv("toneMapping",e.toneMapping):"",e.dithering?"#define DITHERING":"",e.opaque?"#define OPAQUE":"",Nt.colorspace_pars_fragment,_v("linearToOutputTexel",e.outputColorSpace),vv(),e.useDepthPacking?"#define DEPTH_PACKING "+e.depthPacking:"",`
`].filter(Qr).join(`
`)),a=Hl(a),a=Zu(a,e),a=Ju(a,e),o=Hl(o),o=Zu(o,e),o=Ju(o,e),a=ju(a),o=ju(o),e.isRawShaderMaterial!==!0&&(M=`#version 300 es
`,p=[d,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+p,m=["#define varying in",e.glslVersion===mu?"":"layout(location = 0) out highp vec4 pc_fragColor;",e.glslVersion===mu?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+m);const T=M+p+a,S=M+m+o,b=Yu(r,r.VERTEX_SHADER,T),A=Yu(r,r.FRAGMENT_SHADER,S);r.attachShader(g,b),r.attachShader(g,A),e.index0AttributeName!==void 0?r.bindAttribLocation(g,0,e.index0AttributeName):e.morphTargets===!0&&r.bindAttribLocation(g,0,"position"),r.linkProgram(g);function R(D){if(i.debug.checkShaderErrors){const B=r.getProgramInfoLog(g)||"",k=r.getShaderInfoLog(b)||"",X=r.getShaderInfoLog(A)||"",C=B.trim(),L=k.trim(),P=X.trim();let z=!0,O=!0;if(r.getProgramParameter(g,r.LINK_STATUS)===!1)if(z=!1,typeof i.debug.onShaderError=="function")i.debug.onShaderError(r,g,b,A);else{const J=Ku(r,b,"vertex"),Q=Ku(r,A,"fragment");Xt("THREE.WebGLProgram: Shader Error "+r.getError()+" - VALIDATE_STATUS "+r.getProgramParameter(g,r.VALIDATE_STATUS)+`

Material Name: `+D.name+`
Material Type: `+D.type+`

Program Info Log: `+C+`
`+J+`
`+Q)}else C!==""?Pt("WebGLProgram: Program Info Log:",C):(L===""||P==="")&&(O=!1);O&&(D.diagnostics={runnable:z,programLog:C,vertexShader:{log:L,prefix:p},fragmentShader:{log:P,prefix:m}})}r.deleteShader(b),r.deleteShader(A),x=new ha(r,g),y=yv(r,g)}let x;this.getUniforms=function(){return x===void 0&&R(this),x};let y;this.getAttributes=function(){return y===void 0&&R(this),y};let G=e.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return G===!1&&(G=r.getProgramParameter(g,hv)),G},this.destroy=function(){n.releaseStatesOfProgram(this),r.deleteProgram(g),this.program=void 0},this.type=e.shaderType,this.name=e.shaderName,this.id=dv++,this.cacheKey=t,this.usedTimes=1,this.program=g,this.vertexShader=b,this.fragmentShader=A,this}let Bv=0;class kv{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(t){const e=t.vertexShader,n=t.fragmentShader,r=this._getShaderStage(e),s=this._getShaderStage(n),a=this._getShaderCacheForMaterial(t);return a.has(r)===!1&&(a.add(r),r.usedTimes++),a.has(s)===!1&&(a.add(s),s.usedTimes++),this}remove(t){const e=this.materialCache.get(t);for(const n of e)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(t),this}getVertexShaderID(t){return this._getShaderStage(t.vertexShader).id}getFragmentShaderID(t){return this._getShaderStage(t.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(t){const e=this.materialCache;let n=e.get(t);return n===void 0&&(n=new Set,e.set(t,n)),n}_getShaderStage(t){const e=this.shaderCache;let n=e.get(t);return n===void 0&&(n=new zv(t),e.set(t,n)),n}}class zv{constructor(t){this.id=Bv++,this.code=t,this.usedTimes=0}}function Vv(i,t,e,n,r,s){const a=new Hh,o=new kv,l=new Set,c=[],u=new Map,h=n.logarithmicDepthBuffer;let f=n.precision;const d={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distance",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function _(x){return l.add(x),x===0?"uv":`uv${x}`}function g(x,y,G,D,B){const k=D.fog,X=B.geometry,C=x.isMeshStandardMaterial||x.isMeshLambertMaterial||x.isMeshPhongMaterial?D.environment:null,L=x.isMeshStandardMaterial||x.isMeshLambertMaterial&&!x.envMap||x.isMeshPhongMaterial&&!x.envMap,P=t.get(x.envMap||C,L),z=P&&P.mapping===Oa?P.image.height:null,O=d[x.type];x.precision!==null&&(f=n.getMaxPrecision(x.precision),f!==x.precision&&Pt("WebGLProgram.getParameters:",x.precision,"not supported, using",f,"instead."));const J=X.morphAttributes.position||X.morphAttributes.normal||X.morphAttributes.color,Q=J!==void 0?J.length:0;let st=0;X.morphAttributes.position!==void 0&&(st=1),X.morphAttributes.normal!==void 0&&(st=2),X.morphAttributes.color!==void 0&&(st=3);let bt,Ut,Ft,K;if(O){const $t=Tn[O];bt=$t.vertexShader,Ut=$t.fragmentShader}else bt=x.vertexShader,Ut=x.fragmentShader,o.update(x),Ft=o.getVertexShaderID(x),K=o.getFragmentShaderID(x);const nt=i.getRenderTarget(),lt=i.state.buffers.depth.getReversed(),Lt=B.isInstancedMesh===!0,At=B.isBatchedMesh===!0,Rt=!!x.map,ye=!!x.matcap,Gt=!!P,Yt=!!x.aoMap,te=!!x.lightMap,Ot=!!x.bumpMap,he=!!x.normalMap,I=!!x.displacementMap,_e=!!x.emissiveMap,qt=!!x.metalnessMap,re=!!x.roughnessMap,Mt=x.anisotropy>0,w=x.clearcoat>0,v=x.dispersion>0,N=x.iridescence>0,Z=x.sheen>0,j=x.transmission>0,$=Mt&&!!x.anisotropyMap,mt=w&&!!x.clearcoatMap,at=w&&!!x.clearcoatNormalMap,Tt=w&&!!x.clearcoatRoughnessMap,wt=N&&!!x.iridescenceMap,tt=N&&!!x.iridescenceThicknessMap,it=Z&&!!x.sheenColorMap,_t=Z&&!!x.sheenRoughnessMap,xt=!!x.specularMap,ht=!!x.specularColorMap,Bt=!!x.specularIntensityMap,U=j&&!!x.transmissionMap,ot=j&&!!x.thicknessMap,rt=!!x.gradientMap,pt=!!x.alphaMap,et=x.alphaTest>0,Y=!!x.alphaHash,gt=!!x.extensions;let Ct=Cn;x.toneMapped&&(nt===null||nt.isXRRenderTarget===!0)&&(Ct=i.toneMapping);const se={shaderID:O,shaderType:x.type,shaderName:x.name,vertexShader:bt,fragmentShader:Ut,defines:x.defines,customVertexShaderID:Ft,customFragmentShaderID:K,isRawShaderMaterial:x.isRawShaderMaterial===!0,glslVersion:x.glslVersion,precision:f,batching:At,batchingColor:At&&B._colorsTexture!==null,instancing:Lt,instancingColor:Lt&&B.instanceColor!==null,instancingMorph:Lt&&B.morphTexture!==null,outputColorSpace:nt===null?i.outputColorSpace:nt.isXRRenderTarget===!0?nt.texture.colorSpace:Ur,alphaToCoverage:!!x.alphaToCoverage,map:Rt,matcap:ye,envMap:Gt,envMapMode:Gt&&P.mapping,envMapCubeUVHeight:z,aoMap:Yt,lightMap:te,bumpMap:Ot,normalMap:he,displacementMap:I,emissiveMap:_e,normalMapObjectSpace:he&&x.normalMapType===Cm,normalMapTangentSpace:he&&x.normalMapType===Rm,metalnessMap:qt,roughnessMap:re,anisotropy:Mt,anisotropyMap:$,clearcoat:w,clearcoatMap:mt,clearcoatNormalMap:at,clearcoatRoughnessMap:Tt,dispersion:v,iridescence:N,iridescenceMap:wt,iridescenceThicknessMap:tt,sheen:Z,sheenColorMap:it,sheenRoughnessMap:_t,specularMap:xt,specularColorMap:ht,specularIntensityMap:Bt,transmission:j,transmissionMap:U,thicknessMap:ot,gradientMap:rt,opaque:x.transparent===!1&&x.blending===yr&&x.alphaToCoverage===!1,alphaMap:pt,alphaTest:et,alphaHash:Y,combine:x.combine,mapUv:Rt&&_(x.map.channel),aoMapUv:Yt&&_(x.aoMap.channel),lightMapUv:te&&_(x.lightMap.channel),bumpMapUv:Ot&&_(x.bumpMap.channel),normalMapUv:he&&_(x.normalMap.channel),displacementMapUv:I&&_(x.displacementMap.channel),emissiveMapUv:_e&&_(x.emissiveMap.channel),metalnessMapUv:qt&&_(x.metalnessMap.channel),roughnessMapUv:re&&_(x.roughnessMap.channel),anisotropyMapUv:$&&_(x.anisotropyMap.channel),clearcoatMapUv:mt&&_(x.clearcoatMap.channel),clearcoatNormalMapUv:at&&_(x.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:Tt&&_(x.clearcoatRoughnessMap.channel),iridescenceMapUv:wt&&_(x.iridescenceMap.channel),iridescenceThicknessMapUv:tt&&_(x.iridescenceThicknessMap.channel),sheenColorMapUv:it&&_(x.sheenColorMap.channel),sheenRoughnessMapUv:_t&&_(x.sheenRoughnessMap.channel),specularMapUv:xt&&_(x.specularMap.channel),specularColorMapUv:ht&&_(x.specularColorMap.channel),specularIntensityMapUv:Bt&&_(x.specularIntensityMap.channel),transmissionMapUv:U&&_(x.transmissionMap.channel),thicknessMapUv:ot&&_(x.thicknessMap.channel),alphaMapUv:pt&&_(x.alphaMap.channel),vertexTangents:!!X.attributes.tangent&&(he||Mt),vertexColors:x.vertexColors,vertexAlphas:x.vertexColors===!0&&!!X.attributes.color&&X.attributes.color.itemSize===4,pointsUvs:B.isPoints===!0&&!!X.attributes.uv&&(Rt||pt),fog:!!k,useFog:x.fog===!0,fogExp2:!!k&&k.isFogExp2,flatShading:x.wireframe===!1&&(x.flatShading===!0||X.attributes.normal===void 0&&he===!1&&(x.isMeshLambertMaterial||x.isMeshPhongMaterial||x.isMeshStandardMaterial||x.isMeshPhysicalMaterial)),sizeAttenuation:x.sizeAttenuation===!0,logarithmicDepthBuffer:h,reversedDepthBuffer:lt,skinning:B.isSkinnedMesh===!0,morphTargets:X.morphAttributes.position!==void 0,morphNormals:X.morphAttributes.normal!==void 0,morphColors:X.morphAttributes.color!==void 0,morphTargetsCount:Q,morphTextureStride:st,numDirLights:y.directional.length,numPointLights:y.point.length,numSpotLights:y.spot.length,numSpotLightMaps:y.spotLightMap.length,numRectAreaLights:y.rectArea.length,numHemiLights:y.hemi.length,numDirLightShadows:y.directionalShadowMap.length,numPointLightShadows:y.pointShadowMap.length,numSpotLightShadows:y.spotShadowMap.length,numSpotLightShadowsWithMaps:y.numSpotLightShadowsWithMaps,numLightProbes:y.numLightProbes,numClippingPlanes:s.numPlanes,numClipIntersection:s.numIntersection,dithering:x.dithering,shadowMapEnabled:i.shadowMap.enabled&&G.length>0,shadowMapType:i.shadowMap.type,toneMapping:Ct,decodeVideoTexture:Rt&&x.map.isVideoTexture===!0&&Ht.getTransfer(x.map.colorSpace)===Kt,decodeVideoTextureEmissive:_e&&x.emissiveMap.isVideoTexture===!0&&Ht.getTransfer(x.emissiveMap.colorSpace)===Kt,premultipliedAlpha:x.premultipliedAlpha,doubleSided:x.side===$n,flipSided:x.side===We,useDepthPacking:x.depthPacking>=0,depthPacking:x.depthPacking||0,index0AttributeName:x.index0AttributeName,extensionClipCullDistance:gt&&x.extensions.clipCullDistance===!0&&e.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(gt&&x.extensions.multiDraw===!0||At)&&e.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:e.has("KHR_parallel_shader_compile"),customProgramCacheKey:x.customProgramCacheKey()};return se.vertexUv1s=l.has(1),se.vertexUv2s=l.has(2),se.vertexUv3s=l.has(3),l.clear(),se}function p(x){const y=[];if(x.shaderID?y.push(x.shaderID):(y.push(x.customVertexShaderID),y.push(x.customFragmentShaderID)),x.defines!==void 0)for(const G in x.defines)y.push(G),y.push(x.defines[G]);return x.isRawShaderMaterial===!1&&(m(y,x),M(y,x),y.push(i.outputColorSpace)),y.push(x.customProgramCacheKey),y.join()}function m(x,y){x.push(y.precision),x.push(y.outputColorSpace),x.push(y.envMapMode),x.push(y.envMapCubeUVHeight),x.push(y.mapUv),x.push(y.alphaMapUv),x.push(y.lightMapUv),x.push(y.aoMapUv),x.push(y.bumpMapUv),x.push(y.normalMapUv),x.push(y.displacementMapUv),x.push(y.emissiveMapUv),x.push(y.metalnessMapUv),x.push(y.roughnessMapUv),x.push(y.anisotropyMapUv),x.push(y.clearcoatMapUv),x.push(y.clearcoatNormalMapUv),x.push(y.clearcoatRoughnessMapUv),x.push(y.iridescenceMapUv),x.push(y.iridescenceThicknessMapUv),x.push(y.sheenColorMapUv),x.push(y.sheenRoughnessMapUv),x.push(y.specularMapUv),x.push(y.specularColorMapUv),x.push(y.specularIntensityMapUv),x.push(y.transmissionMapUv),x.push(y.thicknessMapUv),x.push(y.combine),x.push(y.fogExp2),x.push(y.sizeAttenuation),x.push(y.morphTargetsCount),x.push(y.morphAttributeCount),x.push(y.numDirLights),x.push(y.numPointLights),x.push(y.numSpotLights),x.push(y.numSpotLightMaps),x.push(y.numHemiLights),x.push(y.numRectAreaLights),x.push(y.numDirLightShadows),x.push(y.numPointLightShadows),x.push(y.numSpotLightShadows),x.push(y.numSpotLightShadowsWithMaps),x.push(y.numLightProbes),x.push(y.shadowMapType),x.push(y.toneMapping),x.push(y.numClippingPlanes),x.push(y.numClipIntersection),x.push(y.depthPacking)}function M(x,y){a.disableAll(),y.instancing&&a.enable(0),y.instancingColor&&a.enable(1),y.instancingMorph&&a.enable(2),y.matcap&&a.enable(3),y.envMap&&a.enable(4),y.normalMapObjectSpace&&a.enable(5),y.normalMapTangentSpace&&a.enable(6),y.clearcoat&&a.enable(7),y.iridescence&&a.enable(8),y.alphaTest&&a.enable(9),y.vertexColors&&a.enable(10),y.vertexAlphas&&a.enable(11),y.vertexUv1s&&a.enable(12),y.vertexUv2s&&a.enable(13),y.vertexUv3s&&a.enable(14),y.vertexTangents&&a.enable(15),y.anisotropy&&a.enable(16),y.alphaHash&&a.enable(17),y.batching&&a.enable(18),y.dispersion&&a.enable(19),y.batchingColor&&a.enable(20),y.gradientMap&&a.enable(21),x.push(a.mask),a.disableAll(),y.fog&&a.enable(0),y.useFog&&a.enable(1),y.flatShading&&a.enable(2),y.logarithmicDepthBuffer&&a.enable(3),y.reversedDepthBuffer&&a.enable(4),y.skinning&&a.enable(5),y.morphTargets&&a.enable(6),y.morphNormals&&a.enable(7),y.morphColors&&a.enable(8),y.premultipliedAlpha&&a.enable(9),y.shadowMapEnabled&&a.enable(10),y.doubleSided&&a.enable(11),y.flipSided&&a.enable(12),y.useDepthPacking&&a.enable(13),y.dithering&&a.enable(14),y.transmission&&a.enable(15),y.sheen&&a.enable(16),y.opaque&&a.enable(17),y.pointsUvs&&a.enable(18),y.decodeVideoTexture&&a.enable(19),y.decodeVideoTextureEmissive&&a.enable(20),y.alphaToCoverage&&a.enable(21),x.push(a.mask)}function T(x){const y=d[x.type];let G;if(y){const D=Tn[y];G=d_.clone(D.uniforms)}else G=x.uniforms;return G}function S(x,y){let G=u.get(y);return G!==void 0?++G.usedTimes:(G=new Ov(i,y,x,r),c.push(G),u.set(y,G)),G}function b(x){if(--x.usedTimes===0){const y=c.indexOf(x);c[y]=c[c.length-1],c.pop(),u.delete(x.cacheKey),x.destroy()}}function A(x){o.remove(x)}function R(){o.dispose()}return{getParameters:g,getProgramCacheKey:p,getUniforms:T,acquireProgram:S,releaseProgram:b,releaseShaderCache:A,programs:c,dispose:R}}function Gv(){let i=new WeakMap;function t(a){return i.has(a)}function e(a){let o=i.get(a);return o===void 0&&(o={},i.set(a,o)),o}function n(a){i.delete(a)}function r(a,o,l){i.get(a)[o]=l}function s(){i=new WeakMap}return{has:t,get:e,remove:n,update:r,dispose:s}}function Hv(i,t){return i.groupOrder!==t.groupOrder?i.groupOrder-t.groupOrder:i.renderOrder!==t.renderOrder?i.renderOrder-t.renderOrder:i.material.id!==t.material.id?i.material.id-t.material.id:i.materialVariant!==t.materialVariant?i.materialVariant-t.materialVariant:i.z!==t.z?i.z-t.z:i.id-t.id}function tf(i,t){return i.groupOrder!==t.groupOrder?i.groupOrder-t.groupOrder:i.renderOrder!==t.renderOrder?i.renderOrder-t.renderOrder:i.z!==t.z?t.z-i.z:i.id-t.id}function ef(){const i=[];let t=0;const e=[],n=[],r=[];function s(){t=0,e.length=0,n.length=0,r.length=0}function a(f){let d=0;return f.isInstancedMesh&&(d+=2),f.isSkinnedMesh&&(d+=1),d}function o(f,d,_,g,p,m){let M=i[t];return M===void 0?(M={id:f.id,object:f,geometry:d,material:_,materialVariant:a(f),groupOrder:g,renderOrder:f.renderOrder,z:p,group:m},i[t]=M):(M.id=f.id,M.object=f,M.geometry=d,M.material=_,M.materialVariant=a(f),M.groupOrder=g,M.renderOrder=f.renderOrder,M.z=p,M.group=m),t++,M}function l(f,d,_,g,p,m){const M=o(f,d,_,g,p,m);_.transmission>0?n.push(M):_.transparent===!0?r.push(M):e.push(M)}function c(f,d,_,g,p,m){const M=o(f,d,_,g,p,m);_.transmission>0?n.unshift(M):_.transparent===!0?r.unshift(M):e.unshift(M)}function u(f,d){e.length>1&&e.sort(f||Hv),n.length>1&&n.sort(d||tf),r.length>1&&r.sort(d||tf)}function h(){for(let f=t,d=i.length;f<d;f++){const _=i[f];if(_.id===null)break;_.id=null,_.object=null,_.geometry=null,_.material=null,_.group=null}}return{opaque:e,transmissive:n,transparent:r,init:s,push:l,unshift:c,finish:h,sort:u}}function Wv(){let i=new WeakMap;function t(n,r){const s=i.get(n);let a;return s===void 0?(a=new ef,i.set(n,[a])):r>=s.length?(a=new ef,s.push(a)):a=s[r],a}function e(){i=new WeakMap}return{get:t,dispose:e}}function Xv(){const i={};return{get:function(t){if(i[t.id]!==void 0)return i[t.id];let e;switch(t.type){case"DirectionalLight":e={direction:new W,color:new Zt};break;case"SpotLight":e={position:new W,direction:new W,color:new Zt,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":e={position:new W,color:new Zt,distance:0,decay:0};break;case"HemisphereLight":e={direction:new W,skyColor:new Zt,groundColor:new Zt};break;case"RectAreaLight":e={color:new Zt,position:new W,halfWidth:new W,halfHeight:new W};break}return i[t.id]=e,e}}}function qv(){const i={};return{get:function(t){if(i[t.id]!==void 0)return i[t.id];let e;switch(t.type){case"DirectionalLight":e={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Qt};break;case"SpotLight":e={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Qt};break;case"PointLight":e={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Qt,shadowCameraNear:1,shadowCameraFar:1e3};break}return i[t.id]=e,e}}}let Yv=0;function $v(i,t){return(t.castShadow?2:0)-(i.castShadow?2:0)+(t.map?1:0)-(i.map?1:0)}function Kv(i){const t=new Xv,e=qv(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let c=0;c<9;c++)n.probe.push(new W);const r=new W,s=new ve,a=new ve;function o(c){let u=0,h=0,f=0;for(let y=0;y<9;y++)n.probe[y].set(0,0,0);let d=0,_=0,g=0,p=0,m=0,M=0,T=0,S=0,b=0,A=0,R=0;c.sort($v);for(let y=0,G=c.length;y<G;y++){const D=c[y],B=D.color,k=D.intensity,X=D.distance;let C=null;if(D.shadow&&D.shadow.map&&(D.shadow.map.texture.format===Ir?C=D.shadow.map.texture:C=D.shadow.map.depthTexture||D.shadow.map.texture),D.isAmbientLight)u+=B.r*k,h+=B.g*k,f+=B.b*k;else if(D.isLightProbe){for(let L=0;L<9;L++)n.probe[L].addScaledVector(D.sh.coefficients[L],k);R++}else if(D.isDirectionalLight){const L=t.get(D);if(L.color.copy(D.color).multiplyScalar(D.intensity),D.castShadow){const P=D.shadow,z=e.get(D);z.shadowIntensity=P.intensity,z.shadowBias=P.bias,z.shadowNormalBias=P.normalBias,z.shadowRadius=P.radius,z.shadowMapSize=P.mapSize,n.directionalShadow[d]=z,n.directionalShadowMap[d]=C,n.directionalShadowMatrix[d]=D.shadow.matrix,M++}n.directional[d]=L,d++}else if(D.isSpotLight){const L=t.get(D);L.position.setFromMatrixPosition(D.matrixWorld),L.color.copy(B).multiplyScalar(k),L.distance=X,L.coneCos=Math.cos(D.angle),L.penumbraCos=Math.cos(D.angle*(1-D.penumbra)),L.decay=D.decay,n.spot[g]=L;const P=D.shadow;if(D.map&&(n.spotLightMap[b]=D.map,b++,P.updateMatrices(D),D.castShadow&&A++),n.spotLightMatrix[g]=P.matrix,D.castShadow){const z=e.get(D);z.shadowIntensity=P.intensity,z.shadowBias=P.bias,z.shadowNormalBias=P.normalBias,z.shadowRadius=P.radius,z.shadowMapSize=P.mapSize,n.spotShadow[g]=z,n.spotShadowMap[g]=C,S++}g++}else if(D.isRectAreaLight){const L=t.get(D);L.color.copy(B).multiplyScalar(k),L.halfWidth.set(D.width*.5,0,0),L.halfHeight.set(0,D.height*.5,0),n.rectArea[p]=L,p++}else if(D.isPointLight){const L=t.get(D);if(L.color.copy(D.color).multiplyScalar(D.intensity),L.distance=D.distance,L.decay=D.decay,D.castShadow){const P=D.shadow,z=e.get(D);z.shadowIntensity=P.intensity,z.shadowBias=P.bias,z.shadowNormalBias=P.normalBias,z.shadowRadius=P.radius,z.shadowMapSize=P.mapSize,z.shadowCameraNear=P.camera.near,z.shadowCameraFar=P.camera.far,n.pointShadow[_]=z,n.pointShadowMap[_]=C,n.pointShadowMatrix[_]=D.shadow.matrix,T++}n.point[_]=L,_++}else if(D.isHemisphereLight){const L=t.get(D);L.skyColor.copy(D.color).multiplyScalar(k),L.groundColor.copy(D.groundColor).multiplyScalar(k),n.hemi[m]=L,m++}}p>0&&(i.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=ct.LTC_FLOAT_1,n.rectAreaLTC2=ct.LTC_FLOAT_2):(n.rectAreaLTC1=ct.LTC_HALF_1,n.rectAreaLTC2=ct.LTC_HALF_2)),n.ambient[0]=u,n.ambient[1]=h,n.ambient[2]=f;const x=n.hash;(x.directionalLength!==d||x.pointLength!==_||x.spotLength!==g||x.rectAreaLength!==p||x.hemiLength!==m||x.numDirectionalShadows!==M||x.numPointShadows!==T||x.numSpotShadows!==S||x.numSpotMaps!==b||x.numLightProbes!==R)&&(n.directional.length=d,n.spot.length=g,n.rectArea.length=p,n.point.length=_,n.hemi.length=m,n.directionalShadow.length=M,n.directionalShadowMap.length=M,n.pointShadow.length=T,n.pointShadowMap.length=T,n.spotShadow.length=S,n.spotShadowMap.length=S,n.directionalShadowMatrix.length=M,n.pointShadowMatrix.length=T,n.spotLightMatrix.length=S+b-A,n.spotLightMap.length=b,n.numSpotLightShadowsWithMaps=A,n.numLightProbes=R,x.directionalLength=d,x.pointLength=_,x.spotLength=g,x.rectAreaLength=p,x.hemiLength=m,x.numDirectionalShadows=M,x.numPointShadows=T,x.numSpotShadows=S,x.numSpotMaps=b,x.numLightProbes=R,n.version=Yv++)}function l(c,u){let h=0,f=0,d=0,_=0,g=0;const p=u.matrixWorldInverse;for(let m=0,M=c.length;m<M;m++){const T=c[m];if(T.isDirectionalLight){const S=n.directional[h];S.direction.setFromMatrixPosition(T.matrixWorld),r.setFromMatrixPosition(T.target.matrixWorld),S.direction.sub(r),S.direction.transformDirection(p),h++}else if(T.isSpotLight){const S=n.spot[d];S.position.setFromMatrixPosition(T.matrixWorld),S.position.applyMatrix4(p),S.direction.setFromMatrixPosition(T.matrixWorld),r.setFromMatrixPosition(T.target.matrixWorld),S.direction.sub(r),S.direction.transformDirection(p),d++}else if(T.isRectAreaLight){const S=n.rectArea[_];S.position.setFromMatrixPosition(T.matrixWorld),S.position.applyMatrix4(p),a.identity(),s.copy(T.matrixWorld),s.premultiply(p),a.extractRotation(s),S.halfWidth.set(T.width*.5,0,0),S.halfHeight.set(0,T.height*.5,0),S.halfWidth.applyMatrix4(a),S.halfHeight.applyMatrix4(a),_++}else if(T.isPointLight){const S=n.point[f];S.position.setFromMatrixPosition(T.matrixWorld),S.position.applyMatrix4(p),f++}else if(T.isHemisphereLight){const S=n.hemi[g];S.direction.setFromMatrixPosition(T.matrixWorld),S.direction.transformDirection(p),g++}}}return{setup:o,setupView:l,state:n}}function nf(i){const t=new Kv(i),e=[],n=[];function r(u){c.camera=u,e.length=0,n.length=0}function s(u){e.push(u)}function a(u){n.push(u)}function o(){t.setup(e)}function l(u){t.setupView(e,u)}const c={lightsArray:e,shadowsArray:n,camera:null,lights:t,transmissionRenderTarget:{}};return{init:r,state:c,setupLights:o,setupLightsView:l,pushLight:s,pushShadow:a}}function Zv(i){let t=new WeakMap;function e(r,s=0){const a=t.get(r);let o;return a===void 0?(o=new nf(i),t.set(r,[o])):s>=a.length?(o=new nf(i),a.push(o)):o=a[s],o}function n(){t=new WeakMap}return{get:e,dispose:n}}const Jv=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,jv=`uniform sampler2D shadow_pass;
uniform vec2 resolution;
uniform float radius;
void main() {
	const float samples = float( VSM_SAMPLES );
	float mean = 0.0;
	float squared_mean = 0.0;
	float uvStride = samples <= 1.0 ? 0.0 : 2.0 / ( samples - 1.0 );
	float uvStart = samples <= 1.0 ? 0.0 : - 1.0;
	for ( float i = 0.0; i < samples; i ++ ) {
		float uvOffset = uvStart + i * uvStride;
		#ifdef HORIZONTAL_PASS
			vec2 distribution = texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( uvOffset, 0.0 ) * radius ) / resolution ).rg;
			mean += distribution.x;
			squared_mean += distribution.y * distribution.y + distribution.x * distribution.x;
		#else
			float depth = texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( 0.0, uvOffset ) * radius ) / resolution ).r;
			mean += depth;
			squared_mean += depth * depth;
		#endif
	}
	mean = mean / samples;
	squared_mean = squared_mean / samples;
	float std_dev = sqrt( max( 0.0, squared_mean - mean * mean ) );
	gl_FragColor = vec4( mean, std_dev, 0.0, 1.0 );
}`,Qv=[new W(1,0,0),new W(-1,0,0),new W(0,1,0),new W(0,-1,0),new W(0,0,1),new W(0,0,-1)],tM=[new W(0,-1,0),new W(0,-1,0),new W(0,0,1),new W(0,0,-1),new W(0,-1,0),new W(0,-1,0)],rf=new ve,$r=new W,Io=new W;function eM(i,t,e){let n=new Yh;const r=new Qt,s=new Qt,a=new me,o=new g_,l=new x_,c={},u=e.maxTextureSize,h={[bi]:We,[We]:bi,[$n]:$n},f=new Fn({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new Qt},radius:{value:4}},vertexShader:Jv,fragmentShader:jv}),d=f.clone();d.defines.HORIZONTAL_PASS=1;const _=new si;_.setAttribute("position",new Dn(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const g=new Nn(_,f),p=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=oa;let m=this.type;this.render=function(A,R,x){if(p.enabled===!1||p.autoUpdate===!1&&p.needsUpdate===!1||A.length===0)return;this.type===sm&&(Pt("WebGLShadowMap: PCFSoftShadowMap has been deprecated. Using PCFShadowMap instead."),this.type=oa);const y=i.getRenderTarget(),G=i.getActiveCubeFace(),D=i.getActiveMipmapLevel(),B=i.state;B.setBlending(Zn),B.buffers.depth.getReversed()===!0?B.buffers.color.setClear(0,0,0,0):B.buffers.color.setClear(1,1,1,1),B.buffers.depth.setTest(!0),B.setScissorTest(!1);const k=m!==this.type;k&&R.traverse(function(X){X.material&&(Array.isArray(X.material)?X.material.forEach(C=>C.needsUpdate=!0):X.material.needsUpdate=!0)});for(let X=0,C=A.length;X<C;X++){const L=A[X],P=L.shadow;if(P===void 0){Pt("WebGLShadowMap:",L,"has no shadow.");continue}if(P.autoUpdate===!1&&P.needsUpdate===!1)continue;r.copy(P.mapSize);const z=P.getFrameExtents();r.multiply(z),s.copy(P.mapSize),(r.x>u||r.y>u)&&(r.x>u&&(s.x=Math.floor(u/z.x),r.x=s.x*z.x,P.mapSize.x=s.x),r.y>u&&(s.y=Math.floor(u/z.y),r.y=s.y*z.y,P.mapSize.y=s.y));const O=i.state.buffers.depth.getReversed();if(P.camera._reversedDepth=O,P.map===null||k===!0){if(P.map!==null&&(P.map.depthTexture!==null&&(P.map.depthTexture.dispose(),P.map.depthTexture=null),P.map.dispose()),this.type===jr){if(L.isPointLight){Pt("WebGLShadowMap: VSM shadow maps are not supported for PointLights. Use PCF or BasicShadowMap instead.");continue}P.map=new Pn(r.x,r.y,{format:Ir,type:ei,minFilter:Ie,magFilter:Ie,generateMipmaps:!1}),P.map.texture.name=L.name+".shadowMap",P.map.depthTexture=new _s(r.x,r.y,wn),P.map.depthTexture.name=L.name+".shadowMapDepth",P.map.depthTexture.format=ni,P.map.depthTexture.compareFunction=null,P.map.depthTexture.minFilter=we,P.map.depthTexture.magFilter=we}else L.isPointLight?(P.map=new td(r.x),P.map.depthTexture=new f_(r.x,Un)):(P.map=new Pn(r.x,r.y),P.map.depthTexture=new _s(r.x,r.y,Un)),P.map.depthTexture.name=L.name+".shadowMap",P.map.depthTexture.format=ni,this.type===oa?(P.map.depthTexture.compareFunction=O?Ac:bc,P.map.depthTexture.minFilter=Ie,P.map.depthTexture.magFilter=Ie):(P.map.depthTexture.compareFunction=null,P.map.depthTexture.minFilter=we,P.map.depthTexture.magFilter=we);P.camera.updateProjectionMatrix()}const J=P.map.isWebGLCubeRenderTarget?6:1;for(let Q=0;Q<J;Q++){if(P.map.isWebGLCubeRenderTarget)i.setRenderTarget(P.map,Q),i.clear();else{Q===0&&(i.setRenderTarget(P.map),i.clear());const st=P.getViewport(Q);a.set(s.x*st.x,s.y*st.y,s.x*st.z,s.y*st.w),B.viewport(a)}if(L.isPointLight){const st=P.camera,bt=P.matrix,Ut=L.distance||st.far;Ut!==st.far&&(st.far=Ut,st.updateProjectionMatrix()),$r.setFromMatrixPosition(L.matrixWorld),st.position.copy($r),Io.copy(st.position),Io.add(Qv[Q]),st.up.copy(tM[Q]),st.lookAt(Io),st.updateMatrixWorld(),bt.makeTranslation(-$r.x,-$r.y,-$r.z),rf.multiplyMatrices(st.projectionMatrix,st.matrixWorldInverse),P._frustum.setFromProjectionMatrix(rf,st.coordinateSystem,st.reversedDepth)}else P.updateMatrices(L);n=P.getFrustum(),S(R,x,P.camera,L,this.type)}P.isPointLightShadow!==!0&&this.type===jr&&M(P,x),P.needsUpdate=!1}m=this.type,p.needsUpdate=!1,i.setRenderTarget(y,G,D)};function M(A,R){const x=t.update(g);f.defines.VSM_SAMPLES!==A.blurSamples&&(f.defines.VSM_SAMPLES=A.blurSamples,d.defines.VSM_SAMPLES=A.blurSamples,f.needsUpdate=!0,d.needsUpdate=!0),A.mapPass===null&&(A.mapPass=new Pn(r.x,r.y,{format:Ir,type:ei})),f.uniforms.shadow_pass.value=A.map.depthTexture,f.uniforms.resolution.value=A.mapSize,f.uniforms.radius.value=A.radius,i.setRenderTarget(A.mapPass),i.clear(),i.renderBufferDirect(R,null,x,f,g,null),d.uniforms.shadow_pass.value=A.mapPass.texture,d.uniforms.resolution.value=A.mapSize,d.uniforms.radius.value=A.radius,i.setRenderTarget(A.map),i.clear(),i.renderBufferDirect(R,null,x,d,g,null)}function T(A,R,x,y){let G=null;const D=x.isPointLight===!0?A.customDistanceMaterial:A.customDepthMaterial;if(D!==void 0)G=D;else if(G=x.isPointLight===!0?l:o,i.localClippingEnabled&&R.clipShadows===!0&&Array.isArray(R.clippingPlanes)&&R.clippingPlanes.length!==0||R.displacementMap&&R.displacementScale!==0||R.alphaMap&&R.alphaTest>0||R.map&&R.alphaTest>0||R.alphaToCoverage===!0){const B=G.uuid,k=R.uuid;let X=c[B];X===void 0&&(X={},c[B]=X);let C=X[k];C===void 0&&(C=G.clone(),X[k]=C,R.addEventListener("dispose",b)),G=C}if(G.visible=R.visible,G.wireframe=R.wireframe,y===jr?G.side=R.shadowSide!==null?R.shadowSide:R.side:G.side=R.shadowSide!==null?R.shadowSide:h[R.side],G.alphaMap=R.alphaMap,G.alphaTest=R.alphaToCoverage===!0?.5:R.alphaTest,G.map=R.map,G.clipShadows=R.clipShadows,G.clippingPlanes=R.clippingPlanes,G.clipIntersection=R.clipIntersection,G.displacementMap=R.displacementMap,G.displacementScale=R.displacementScale,G.displacementBias=R.displacementBias,G.wireframeLinewidth=R.wireframeLinewidth,G.linewidth=R.linewidth,x.isPointLight===!0&&G.isMeshDistanceMaterial===!0){const B=i.properties.get(G);B.light=x}return G}function S(A,R,x,y,G){if(A.visible===!1)return;if(A.layers.test(R.layers)&&(A.isMesh||A.isLine||A.isPoints)&&(A.castShadow||A.receiveShadow&&G===jr)&&(!A.frustumCulled||n.intersectsObject(A))){A.modelViewMatrix.multiplyMatrices(x.matrixWorldInverse,A.matrixWorld);const k=t.update(A),X=A.material;if(Array.isArray(X)){const C=k.groups;for(let L=0,P=C.length;L<P;L++){const z=C[L],O=X[z.materialIndex];if(O&&O.visible){const J=T(A,O,y,G);A.onBeforeShadow(i,A,R,x,k,J,z),i.renderBufferDirect(x,null,k,J,A,z),A.onAfterShadow(i,A,R,x,k,J,z)}}}else if(X.visible){const C=T(A,X,y,G);A.onBeforeShadow(i,A,R,x,k,C,null),i.renderBufferDirect(x,null,k,C,A,null),A.onAfterShadow(i,A,R,x,k,C,null)}}const B=A.children;for(let k=0,X=B.length;k<X;k++)S(B[k],R,x,y,G)}function b(A){A.target.removeEventListener("dispose",b);for(const x in c){const y=c[x],G=A.target.uuid;G in y&&(y[G].dispose(),delete y[G])}}}function nM(i,t){function e(){let U=!1;const ot=new me;let rt=null;const pt=new me(0,0,0,0);return{setMask:function(et){rt!==et&&!U&&(i.colorMask(et,et,et,et),rt=et)},setLocked:function(et){U=et},setClear:function(et,Y,gt,Ct,se){se===!0&&(et*=Ct,Y*=Ct,gt*=Ct),ot.set(et,Y,gt,Ct),pt.equals(ot)===!1&&(i.clearColor(et,Y,gt,Ct),pt.copy(ot))},reset:function(){U=!1,rt=null,pt.set(-1,0,0,0)}}}function n(){let U=!1,ot=!1,rt=null,pt=null,et=null;return{setReversed:function(Y){if(ot!==Y){const gt=t.get("EXT_clip_control");Y?gt.clipControlEXT(gt.LOWER_LEFT_EXT,gt.ZERO_TO_ONE_EXT):gt.clipControlEXT(gt.LOWER_LEFT_EXT,gt.NEGATIVE_ONE_TO_ONE_EXT),ot=Y;const Ct=et;et=null,this.setClear(Ct)}},getReversed:function(){return ot},setTest:function(Y){Y?nt(i.DEPTH_TEST):lt(i.DEPTH_TEST)},setMask:function(Y){rt!==Y&&!U&&(i.depthMask(Y),rt=Y)},setFunc:function(Y){if(ot&&(Y=km[Y]),pt!==Y){switch(Y){case tl:i.depthFunc(i.NEVER);break;case el:i.depthFunc(i.ALWAYS);break;case nl:i.depthFunc(i.LESS);break;case Dr:i.depthFunc(i.LEQUAL);break;case il:i.depthFunc(i.EQUAL);break;case rl:i.depthFunc(i.GEQUAL);break;case sl:i.depthFunc(i.GREATER);break;case al:i.depthFunc(i.NOTEQUAL);break;default:i.depthFunc(i.LEQUAL)}pt=Y}},setLocked:function(Y){U=Y},setClear:function(Y){et!==Y&&(et=Y,ot&&(Y=1-Y),i.clearDepth(Y))},reset:function(){U=!1,rt=null,pt=null,et=null,ot=!1}}}function r(){let U=!1,ot=null,rt=null,pt=null,et=null,Y=null,gt=null,Ct=null,se=null;return{setTest:function($t){U||($t?nt(i.STENCIL_TEST):lt(i.STENCIL_TEST))},setMask:function($t){ot!==$t&&!U&&(i.stencilMask($t),ot=$t)},setFunc:function($t,Bn,kn){(rt!==$t||pt!==Bn||et!==kn)&&(i.stencilFunc($t,Bn,kn),rt=$t,pt=Bn,et=kn)},setOp:function($t,Bn,kn){(Y!==$t||gt!==Bn||Ct!==kn)&&(i.stencilOp($t,Bn,kn),Y=$t,gt=Bn,Ct=kn)},setLocked:function($t){U=$t},setClear:function($t){se!==$t&&(i.clearStencil($t),se=$t)},reset:function(){U=!1,ot=null,rt=null,pt=null,et=null,Y=null,gt=null,Ct=null,se=null}}}const s=new e,a=new n,o=new r,l=new WeakMap,c=new WeakMap;let u={},h={},f=new WeakMap,d=[],_=null,g=!1,p=null,m=null,M=null,T=null,S=null,b=null,A=null,R=new Zt(0,0,0),x=0,y=!1,G=null,D=null,B=null,k=null,X=null;const C=i.getParameter(i.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let L=!1,P=0;const z=i.getParameter(i.VERSION);z.indexOf("WebGL")!==-1?(P=parseFloat(/^WebGL (\d)/.exec(z)[1]),L=P>=1):z.indexOf("OpenGL ES")!==-1&&(P=parseFloat(/^OpenGL ES (\d)/.exec(z)[1]),L=P>=2);let O=null,J={};const Q=i.getParameter(i.SCISSOR_BOX),st=i.getParameter(i.VIEWPORT),bt=new me().fromArray(Q),Ut=new me().fromArray(st);function Ft(U,ot,rt,pt){const et=new Uint8Array(4),Y=i.createTexture();i.bindTexture(U,Y),i.texParameteri(U,i.TEXTURE_MIN_FILTER,i.NEAREST),i.texParameteri(U,i.TEXTURE_MAG_FILTER,i.NEAREST);for(let gt=0;gt<rt;gt++)U===i.TEXTURE_3D||U===i.TEXTURE_2D_ARRAY?i.texImage3D(ot,0,i.RGBA,1,1,pt,0,i.RGBA,i.UNSIGNED_BYTE,et):i.texImage2D(ot+gt,0,i.RGBA,1,1,0,i.RGBA,i.UNSIGNED_BYTE,et);return Y}const K={};K[i.TEXTURE_2D]=Ft(i.TEXTURE_2D,i.TEXTURE_2D,1),K[i.TEXTURE_CUBE_MAP]=Ft(i.TEXTURE_CUBE_MAP,i.TEXTURE_CUBE_MAP_POSITIVE_X,6),K[i.TEXTURE_2D_ARRAY]=Ft(i.TEXTURE_2D_ARRAY,i.TEXTURE_2D_ARRAY,1,1),K[i.TEXTURE_3D]=Ft(i.TEXTURE_3D,i.TEXTURE_3D,1,1),s.setClear(0,0,0,1),a.setClear(1),o.setClear(0),nt(i.DEPTH_TEST),a.setFunc(Dr),Ot(!1),he(cu),nt(i.CULL_FACE),Yt(Zn);function nt(U){u[U]!==!0&&(i.enable(U),u[U]=!0)}function lt(U){u[U]!==!1&&(i.disable(U),u[U]=!1)}function Lt(U,ot){return h[U]!==ot?(i.bindFramebuffer(U,ot),h[U]=ot,U===i.DRAW_FRAMEBUFFER&&(h[i.FRAMEBUFFER]=ot),U===i.FRAMEBUFFER&&(h[i.DRAW_FRAMEBUFFER]=ot),!0):!1}function At(U,ot){let rt=d,pt=!1;if(U){rt=f.get(ot),rt===void 0&&(rt=[],f.set(ot,rt));const et=U.textures;if(rt.length!==et.length||rt[0]!==i.COLOR_ATTACHMENT0){for(let Y=0,gt=et.length;Y<gt;Y++)rt[Y]=i.COLOR_ATTACHMENT0+Y;rt.length=et.length,pt=!0}}else rt[0]!==i.BACK&&(rt[0]=i.BACK,pt=!0);pt&&i.drawBuffers(rt)}function Rt(U){return _!==U?(i.useProgram(U),_=U,!0):!1}const ye={[zi]:i.FUNC_ADD,[om]:i.FUNC_SUBTRACT,[lm]:i.FUNC_REVERSE_SUBTRACT};ye[cm]=i.MIN,ye[um]=i.MAX;const Gt={[fm]:i.ZERO,[hm]:i.ONE,[dm]:i.SRC_COLOR,[jo]:i.SRC_ALPHA,[vm]:i.SRC_ALPHA_SATURATE,[gm]:i.DST_COLOR,[mm]:i.DST_ALPHA,[pm]:i.ONE_MINUS_SRC_COLOR,[Qo]:i.ONE_MINUS_SRC_ALPHA,[xm]:i.ONE_MINUS_DST_COLOR,[_m]:i.ONE_MINUS_DST_ALPHA,[Mm]:i.CONSTANT_COLOR,[Sm]:i.ONE_MINUS_CONSTANT_COLOR,[ym]:i.CONSTANT_ALPHA,[Em]:i.ONE_MINUS_CONSTANT_ALPHA};function Yt(U,ot,rt,pt,et,Y,gt,Ct,se,$t){if(U===Zn){g===!0&&(lt(i.BLEND),g=!1);return}if(g===!1&&(nt(i.BLEND),g=!0),U!==am){if(U!==p||$t!==y){if((m!==zi||S!==zi)&&(i.blendEquation(i.FUNC_ADD),m=zi,S=zi),$t)switch(U){case yr:i.blendFuncSeparate(i.ONE,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case uu:i.blendFunc(i.ONE,i.ONE);break;case fu:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case hu:i.blendFuncSeparate(i.DST_COLOR,i.ONE_MINUS_SRC_ALPHA,i.ZERO,i.ONE);break;default:Xt("WebGLState: Invalid blending: ",U);break}else switch(U){case yr:i.blendFuncSeparate(i.SRC_ALPHA,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case uu:i.blendFuncSeparate(i.SRC_ALPHA,i.ONE,i.ONE,i.ONE);break;case fu:Xt("WebGLState: SubtractiveBlending requires material.premultipliedAlpha = true");break;case hu:Xt("WebGLState: MultiplyBlending requires material.premultipliedAlpha = true");break;default:Xt("WebGLState: Invalid blending: ",U);break}M=null,T=null,b=null,A=null,R.set(0,0,0),x=0,p=U,y=$t}return}et=et||ot,Y=Y||rt,gt=gt||pt,(ot!==m||et!==S)&&(i.blendEquationSeparate(ye[ot],ye[et]),m=ot,S=et),(rt!==M||pt!==T||Y!==b||gt!==A)&&(i.blendFuncSeparate(Gt[rt],Gt[pt],Gt[Y],Gt[gt]),M=rt,T=pt,b=Y,A=gt),(Ct.equals(R)===!1||se!==x)&&(i.blendColor(Ct.r,Ct.g,Ct.b,se),R.copy(Ct),x=se),p=U,y=!1}function te(U,ot){U.side===$n?lt(i.CULL_FACE):nt(i.CULL_FACE);let rt=U.side===We;ot&&(rt=!rt),Ot(rt),U.blending===yr&&U.transparent===!1?Yt(Zn):Yt(U.blending,U.blendEquation,U.blendSrc,U.blendDst,U.blendEquationAlpha,U.blendSrcAlpha,U.blendDstAlpha,U.blendColor,U.blendAlpha,U.premultipliedAlpha),a.setFunc(U.depthFunc),a.setTest(U.depthTest),a.setMask(U.depthWrite),s.setMask(U.colorWrite);const pt=U.stencilWrite;o.setTest(pt),pt&&(o.setMask(U.stencilWriteMask),o.setFunc(U.stencilFunc,U.stencilRef,U.stencilFuncMask),o.setOp(U.stencilFail,U.stencilZFail,U.stencilZPass)),_e(U.polygonOffset,U.polygonOffsetFactor,U.polygonOffsetUnits),U.alphaToCoverage===!0?nt(i.SAMPLE_ALPHA_TO_COVERAGE):lt(i.SAMPLE_ALPHA_TO_COVERAGE)}function Ot(U){G!==U&&(U?i.frontFace(i.CW):i.frontFace(i.CCW),G=U)}function he(U){U!==im?(nt(i.CULL_FACE),U!==D&&(U===cu?i.cullFace(i.BACK):U===rm?i.cullFace(i.FRONT):i.cullFace(i.FRONT_AND_BACK))):lt(i.CULL_FACE),D=U}function I(U){U!==B&&(L&&i.lineWidth(U),B=U)}function _e(U,ot,rt){U?(nt(i.POLYGON_OFFSET_FILL),(k!==ot||X!==rt)&&(k=ot,X=rt,a.getReversed()&&(ot=-ot),i.polygonOffset(ot,rt))):lt(i.POLYGON_OFFSET_FILL)}function qt(U){U?nt(i.SCISSOR_TEST):lt(i.SCISSOR_TEST)}function re(U){U===void 0&&(U=i.TEXTURE0+C-1),O!==U&&(i.activeTexture(U),O=U)}function Mt(U,ot,rt){rt===void 0&&(O===null?rt=i.TEXTURE0+C-1:rt=O);let pt=J[rt];pt===void 0&&(pt={type:void 0,texture:void 0},J[rt]=pt),(pt.type!==U||pt.texture!==ot)&&(O!==rt&&(i.activeTexture(rt),O=rt),i.bindTexture(U,ot||K[U]),pt.type=U,pt.texture=ot)}function w(){const U=J[O];U!==void 0&&U.type!==void 0&&(i.bindTexture(U.type,null),U.type=void 0,U.texture=void 0)}function v(){try{i.compressedTexImage2D(...arguments)}catch(U){Xt("WebGLState:",U)}}function N(){try{i.compressedTexImage3D(...arguments)}catch(U){Xt("WebGLState:",U)}}function Z(){try{i.texSubImage2D(...arguments)}catch(U){Xt("WebGLState:",U)}}function j(){try{i.texSubImage3D(...arguments)}catch(U){Xt("WebGLState:",U)}}function $(){try{i.compressedTexSubImage2D(...arguments)}catch(U){Xt("WebGLState:",U)}}function mt(){try{i.compressedTexSubImage3D(...arguments)}catch(U){Xt("WebGLState:",U)}}function at(){try{i.texStorage2D(...arguments)}catch(U){Xt("WebGLState:",U)}}function Tt(){try{i.texStorage3D(...arguments)}catch(U){Xt("WebGLState:",U)}}function wt(){try{i.texImage2D(...arguments)}catch(U){Xt("WebGLState:",U)}}function tt(){try{i.texImage3D(...arguments)}catch(U){Xt("WebGLState:",U)}}function it(U){bt.equals(U)===!1&&(i.scissor(U.x,U.y,U.z,U.w),bt.copy(U))}function _t(U){Ut.equals(U)===!1&&(i.viewport(U.x,U.y,U.z,U.w),Ut.copy(U))}function xt(U,ot){let rt=c.get(ot);rt===void 0&&(rt=new WeakMap,c.set(ot,rt));let pt=rt.get(U);pt===void 0&&(pt=i.getUniformBlockIndex(ot,U.name),rt.set(U,pt))}function ht(U,ot){const pt=c.get(ot).get(U);l.get(ot)!==pt&&(i.uniformBlockBinding(ot,pt,U.__bindingPointIndex),l.set(ot,pt))}function Bt(){i.disable(i.BLEND),i.disable(i.CULL_FACE),i.disable(i.DEPTH_TEST),i.disable(i.POLYGON_OFFSET_FILL),i.disable(i.SCISSOR_TEST),i.disable(i.STENCIL_TEST),i.disable(i.SAMPLE_ALPHA_TO_COVERAGE),i.blendEquation(i.FUNC_ADD),i.blendFunc(i.ONE,i.ZERO),i.blendFuncSeparate(i.ONE,i.ZERO,i.ONE,i.ZERO),i.blendColor(0,0,0,0),i.colorMask(!0,!0,!0,!0),i.clearColor(0,0,0,0),i.depthMask(!0),i.depthFunc(i.LESS),a.setReversed(!1),i.clearDepth(1),i.stencilMask(4294967295),i.stencilFunc(i.ALWAYS,0,4294967295),i.stencilOp(i.KEEP,i.KEEP,i.KEEP),i.clearStencil(0),i.cullFace(i.BACK),i.frontFace(i.CCW),i.polygonOffset(0,0),i.activeTexture(i.TEXTURE0),i.bindFramebuffer(i.FRAMEBUFFER,null),i.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),i.bindFramebuffer(i.READ_FRAMEBUFFER,null),i.useProgram(null),i.lineWidth(1),i.scissor(0,0,i.canvas.width,i.canvas.height),i.viewport(0,0,i.canvas.width,i.canvas.height),u={},O=null,J={},h={},f=new WeakMap,d=[],_=null,g=!1,p=null,m=null,M=null,T=null,S=null,b=null,A=null,R=new Zt(0,0,0),x=0,y=!1,G=null,D=null,B=null,k=null,X=null,bt.set(0,0,i.canvas.width,i.canvas.height),Ut.set(0,0,i.canvas.width,i.canvas.height),s.reset(),a.reset(),o.reset()}return{buffers:{color:s,depth:a,stencil:o},enable:nt,disable:lt,bindFramebuffer:Lt,drawBuffers:At,useProgram:Rt,setBlending:Yt,setMaterial:te,setFlipSided:Ot,setCullFace:he,setLineWidth:I,setPolygonOffset:_e,setScissorTest:qt,activeTexture:re,bindTexture:Mt,unbindTexture:w,compressedTexImage2D:v,compressedTexImage3D:N,texImage2D:wt,texImage3D:tt,updateUBOMapping:xt,uniformBlockBinding:ht,texStorage2D:at,texStorage3D:Tt,texSubImage2D:Z,texSubImage3D:j,compressedTexSubImage2D:$,compressedTexSubImage3D:mt,scissor:it,viewport:_t,reset:Bt}}function iM(i,t,e,n,r,s,a){const o=t.has("WEBGL_multisampled_render_to_texture")?t.get("WEBGL_multisampled_render_to_texture"):null,l=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),c=new Qt,u=new WeakMap;let h;const f=new WeakMap;let d=!1;try{d=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function _(w,v){return d?new OffscreenCanvas(w,v):ba("canvas")}function g(w,v,N){let Z=1;const j=Mt(w);if((j.width>N||j.height>N)&&(Z=N/Math.max(j.width,j.height)),Z<1)if(typeof HTMLImageElement<"u"&&w instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&w instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&w instanceof ImageBitmap||typeof VideoFrame<"u"&&w instanceof VideoFrame){const $=Math.floor(Z*j.width),mt=Math.floor(Z*j.height);h===void 0&&(h=_($,mt));const at=v?_($,mt):h;return at.width=$,at.height=mt,at.getContext("2d").drawImage(w,0,0,$,mt),Pt("WebGLRenderer: Texture has been resized from ("+j.width+"x"+j.height+") to ("+$+"x"+mt+")."),at}else return"data"in w&&Pt("WebGLRenderer: Image in DataTexture is too big ("+j.width+"x"+j.height+")."),w;return w}function p(w){return w.generateMipmaps}function m(w){i.generateMipmap(w)}function M(w){return w.isWebGLCubeRenderTarget?i.TEXTURE_CUBE_MAP:w.isWebGL3DRenderTarget?i.TEXTURE_3D:w.isWebGLArrayRenderTarget||w.isCompressedArrayTexture?i.TEXTURE_2D_ARRAY:i.TEXTURE_2D}function T(w,v,N,Z,j=!1){if(w!==null){if(i[w]!==void 0)return i[w];Pt("WebGLRenderer: Attempt to use non-existing WebGL internal format '"+w+"'")}let $=v;if(v===i.RED&&(N===i.FLOAT&&($=i.R32F),N===i.HALF_FLOAT&&($=i.R16F),N===i.UNSIGNED_BYTE&&($=i.R8)),v===i.RED_INTEGER&&(N===i.UNSIGNED_BYTE&&($=i.R8UI),N===i.UNSIGNED_SHORT&&($=i.R16UI),N===i.UNSIGNED_INT&&($=i.R32UI),N===i.BYTE&&($=i.R8I),N===i.SHORT&&($=i.R16I),N===i.INT&&($=i.R32I)),v===i.RG&&(N===i.FLOAT&&($=i.RG32F),N===i.HALF_FLOAT&&($=i.RG16F),N===i.UNSIGNED_BYTE&&($=i.RG8)),v===i.RG_INTEGER&&(N===i.UNSIGNED_BYTE&&($=i.RG8UI),N===i.UNSIGNED_SHORT&&($=i.RG16UI),N===i.UNSIGNED_INT&&($=i.RG32UI),N===i.BYTE&&($=i.RG8I),N===i.SHORT&&($=i.RG16I),N===i.INT&&($=i.RG32I)),v===i.RGB_INTEGER&&(N===i.UNSIGNED_BYTE&&($=i.RGB8UI),N===i.UNSIGNED_SHORT&&($=i.RGB16UI),N===i.UNSIGNED_INT&&($=i.RGB32UI),N===i.BYTE&&($=i.RGB8I),N===i.SHORT&&($=i.RGB16I),N===i.INT&&($=i.RGB32I)),v===i.RGBA_INTEGER&&(N===i.UNSIGNED_BYTE&&($=i.RGBA8UI),N===i.UNSIGNED_SHORT&&($=i.RGBA16UI),N===i.UNSIGNED_INT&&($=i.RGBA32UI),N===i.BYTE&&($=i.RGBA8I),N===i.SHORT&&($=i.RGBA16I),N===i.INT&&($=i.RGBA32I)),v===i.RGB&&(N===i.UNSIGNED_INT_5_9_9_9_REV&&($=i.RGB9_E5),N===i.UNSIGNED_INT_10F_11F_11F_REV&&($=i.R11F_G11F_B10F)),v===i.RGBA){const mt=j?Ea:Ht.getTransfer(Z);N===i.FLOAT&&($=i.RGBA32F),N===i.HALF_FLOAT&&($=i.RGBA16F),N===i.UNSIGNED_BYTE&&($=mt===Kt?i.SRGB8_ALPHA8:i.RGBA8),N===i.UNSIGNED_SHORT_4_4_4_4&&($=i.RGBA4),N===i.UNSIGNED_SHORT_5_5_5_1&&($=i.RGB5_A1)}return($===i.R16F||$===i.R32F||$===i.RG16F||$===i.RG32F||$===i.RGBA16F||$===i.RGBA32F)&&t.get("EXT_color_buffer_float"),$}function S(w,v){let N;return w?v===null||v===Un||v===ms?N=i.DEPTH24_STENCIL8:v===wn?N=i.DEPTH32F_STENCIL8:v===ps&&(N=i.DEPTH24_STENCIL8,Pt("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):v===null||v===Un||v===ms?N=i.DEPTH_COMPONENT24:v===wn?N=i.DEPTH_COMPONENT32F:v===ps&&(N=i.DEPTH_COMPONENT16),N}function b(w,v){return p(w)===!0||w.isFramebufferTexture&&w.minFilter!==we&&w.minFilter!==Ie?Math.log2(Math.max(v.width,v.height))+1:w.mipmaps!==void 0&&w.mipmaps.length>0?w.mipmaps.length:w.isCompressedTexture&&Array.isArray(w.image)?v.mipmaps.length:1}function A(w){const v=w.target;v.removeEventListener("dispose",A),x(v),v.isVideoTexture&&u.delete(v)}function R(w){const v=w.target;v.removeEventListener("dispose",R),G(v)}function x(w){const v=n.get(w);if(v.__webglInit===void 0)return;const N=w.source,Z=f.get(N);if(Z){const j=Z[v.__cacheKey];j.usedTimes--,j.usedTimes===0&&y(w),Object.keys(Z).length===0&&f.delete(N)}n.remove(w)}function y(w){const v=n.get(w);i.deleteTexture(v.__webglTexture);const N=w.source,Z=f.get(N);delete Z[v.__cacheKey],a.memory.textures--}function G(w){const v=n.get(w);if(w.depthTexture&&(w.depthTexture.dispose(),n.remove(w.depthTexture)),w.isWebGLCubeRenderTarget)for(let Z=0;Z<6;Z++){if(Array.isArray(v.__webglFramebuffer[Z]))for(let j=0;j<v.__webglFramebuffer[Z].length;j++)i.deleteFramebuffer(v.__webglFramebuffer[Z][j]);else i.deleteFramebuffer(v.__webglFramebuffer[Z]);v.__webglDepthbuffer&&i.deleteRenderbuffer(v.__webglDepthbuffer[Z])}else{if(Array.isArray(v.__webglFramebuffer))for(let Z=0;Z<v.__webglFramebuffer.length;Z++)i.deleteFramebuffer(v.__webglFramebuffer[Z]);else i.deleteFramebuffer(v.__webglFramebuffer);if(v.__webglDepthbuffer&&i.deleteRenderbuffer(v.__webglDepthbuffer),v.__webglMultisampledFramebuffer&&i.deleteFramebuffer(v.__webglMultisampledFramebuffer),v.__webglColorRenderbuffer)for(let Z=0;Z<v.__webglColorRenderbuffer.length;Z++)v.__webglColorRenderbuffer[Z]&&i.deleteRenderbuffer(v.__webglColorRenderbuffer[Z]);v.__webglDepthRenderbuffer&&i.deleteRenderbuffer(v.__webglDepthRenderbuffer)}const N=w.textures;for(let Z=0,j=N.length;Z<j;Z++){const $=n.get(N[Z]);$.__webglTexture&&(i.deleteTexture($.__webglTexture),a.memory.textures--),n.remove(N[Z])}n.remove(w)}let D=0;function B(){D=0}function k(){const w=D;return w>=r.maxTextures&&Pt("WebGLTextures: Trying to use "+w+" texture units while this GPU supports only "+r.maxTextures),D+=1,w}function X(w){const v=[];return v.push(w.wrapS),v.push(w.wrapT),v.push(w.wrapR||0),v.push(w.magFilter),v.push(w.minFilter),v.push(w.anisotropy),v.push(w.internalFormat),v.push(w.format),v.push(w.type),v.push(w.generateMipmaps),v.push(w.premultiplyAlpha),v.push(w.flipY),v.push(w.unpackAlignment),v.push(w.colorSpace),v.join()}function C(w,v){const N=n.get(w);if(w.isVideoTexture&&qt(w),w.isRenderTargetTexture===!1&&w.isExternalTexture!==!0&&w.version>0&&N.__version!==w.version){const Z=w.image;if(Z===null)Pt("WebGLRenderer: Texture marked for update but no image data found.");else if(Z.complete===!1)Pt("WebGLRenderer: Texture marked for update but image is incomplete");else{K(N,w,v);return}}else w.isExternalTexture&&(N.__webglTexture=w.sourceTexture?w.sourceTexture:null);e.bindTexture(i.TEXTURE_2D,N.__webglTexture,i.TEXTURE0+v)}function L(w,v){const N=n.get(w);if(w.isRenderTargetTexture===!1&&w.version>0&&N.__version!==w.version){K(N,w,v);return}else w.isExternalTexture&&(N.__webglTexture=w.sourceTexture?w.sourceTexture:null);e.bindTexture(i.TEXTURE_2D_ARRAY,N.__webglTexture,i.TEXTURE0+v)}function P(w,v){const N=n.get(w);if(w.isRenderTargetTexture===!1&&w.version>0&&N.__version!==w.version){K(N,w,v);return}e.bindTexture(i.TEXTURE_3D,N.__webglTexture,i.TEXTURE0+v)}function z(w,v){const N=n.get(w);if(w.isCubeDepthTexture!==!0&&w.version>0&&N.__version!==w.version){nt(N,w,v);return}e.bindTexture(i.TEXTURE_CUBE_MAP,N.__webglTexture,i.TEXTURE0+v)}const O={[ol]:i.REPEAT,[Kn]:i.CLAMP_TO_EDGE,[ll]:i.MIRRORED_REPEAT},J={[we]:i.NEAREST,[Am]:i.NEAREST_MIPMAP_NEAREST,[Ds]:i.NEAREST_MIPMAP_LINEAR,[Ie]:i.LINEAR,[no]:i.LINEAR_MIPMAP_NEAREST,[Hi]:i.LINEAR_MIPMAP_LINEAR},Q={[Pm]:i.NEVER,[Nm]:i.ALWAYS,[Dm]:i.LESS,[bc]:i.LEQUAL,[Lm]:i.EQUAL,[Ac]:i.GEQUAL,[Im]:i.GREATER,[Um]:i.NOTEQUAL};function st(w,v){if(v.type===wn&&t.has("OES_texture_float_linear")===!1&&(v.magFilter===Ie||v.magFilter===no||v.magFilter===Ds||v.magFilter===Hi||v.minFilter===Ie||v.minFilter===no||v.minFilter===Ds||v.minFilter===Hi)&&Pt("WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),i.texParameteri(w,i.TEXTURE_WRAP_S,O[v.wrapS]),i.texParameteri(w,i.TEXTURE_WRAP_T,O[v.wrapT]),(w===i.TEXTURE_3D||w===i.TEXTURE_2D_ARRAY)&&i.texParameteri(w,i.TEXTURE_WRAP_R,O[v.wrapR]),i.texParameteri(w,i.TEXTURE_MAG_FILTER,J[v.magFilter]),i.texParameteri(w,i.TEXTURE_MIN_FILTER,J[v.minFilter]),v.compareFunction&&(i.texParameteri(w,i.TEXTURE_COMPARE_MODE,i.COMPARE_REF_TO_TEXTURE),i.texParameteri(w,i.TEXTURE_COMPARE_FUNC,Q[v.compareFunction])),t.has("EXT_texture_filter_anisotropic")===!0){if(v.magFilter===we||v.minFilter!==Ds&&v.minFilter!==Hi||v.type===wn&&t.has("OES_texture_float_linear")===!1)return;if(v.anisotropy>1||n.get(v).__currentAnisotropy){const N=t.get("EXT_texture_filter_anisotropic");i.texParameterf(w,N.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(v.anisotropy,r.getMaxAnisotropy())),n.get(v).__currentAnisotropy=v.anisotropy}}}function bt(w,v){let N=!1;w.__webglInit===void 0&&(w.__webglInit=!0,v.addEventListener("dispose",A));const Z=v.source;let j=f.get(Z);j===void 0&&(j={},f.set(Z,j));const $=X(v);if($!==w.__cacheKey){j[$]===void 0&&(j[$]={texture:i.createTexture(),usedTimes:0},a.memory.textures++,N=!0),j[$].usedTimes++;const mt=j[w.__cacheKey];mt!==void 0&&(j[w.__cacheKey].usedTimes--,mt.usedTimes===0&&y(v)),w.__cacheKey=$,w.__webglTexture=j[$].texture}return N}function Ut(w,v,N){return Math.floor(Math.floor(w/N)/v)}function Ft(w,v,N,Z){const $=w.updateRanges;if($.length===0)e.texSubImage2D(i.TEXTURE_2D,0,0,0,v.width,v.height,N,Z,v.data);else{$.sort((tt,it)=>tt.start-it.start);let mt=0;for(let tt=1;tt<$.length;tt++){const it=$[mt],_t=$[tt],xt=it.start+it.count,ht=Ut(_t.start,v.width,4),Bt=Ut(it.start,v.width,4);_t.start<=xt+1&&ht===Bt&&Ut(_t.start+_t.count-1,v.width,4)===ht?it.count=Math.max(it.count,_t.start+_t.count-it.start):(++mt,$[mt]=_t)}$.length=mt+1;const at=i.getParameter(i.UNPACK_ROW_LENGTH),Tt=i.getParameter(i.UNPACK_SKIP_PIXELS),wt=i.getParameter(i.UNPACK_SKIP_ROWS);i.pixelStorei(i.UNPACK_ROW_LENGTH,v.width);for(let tt=0,it=$.length;tt<it;tt++){const _t=$[tt],xt=Math.floor(_t.start/4),ht=Math.ceil(_t.count/4),Bt=xt%v.width,U=Math.floor(xt/v.width),ot=ht,rt=1;i.pixelStorei(i.UNPACK_SKIP_PIXELS,Bt),i.pixelStorei(i.UNPACK_SKIP_ROWS,U),e.texSubImage2D(i.TEXTURE_2D,0,Bt,U,ot,rt,N,Z,v.data)}w.clearUpdateRanges(),i.pixelStorei(i.UNPACK_ROW_LENGTH,at),i.pixelStorei(i.UNPACK_SKIP_PIXELS,Tt),i.pixelStorei(i.UNPACK_SKIP_ROWS,wt)}}function K(w,v,N){let Z=i.TEXTURE_2D;(v.isDataArrayTexture||v.isCompressedArrayTexture)&&(Z=i.TEXTURE_2D_ARRAY),v.isData3DTexture&&(Z=i.TEXTURE_3D);const j=bt(w,v),$=v.source;e.bindTexture(Z,w.__webglTexture,i.TEXTURE0+N);const mt=n.get($);if($.version!==mt.__version||j===!0){e.activeTexture(i.TEXTURE0+N);const at=Ht.getPrimaries(Ht.workingColorSpace),Tt=v.colorSpace===mi?null:Ht.getPrimaries(v.colorSpace),wt=v.colorSpace===mi||at===Tt?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,v.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,v.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,v.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,wt);let tt=g(v.image,!1,r.maxTextureSize);tt=re(v,tt);const it=s.convert(v.format,v.colorSpace),_t=s.convert(v.type);let xt=T(v.internalFormat,it,_t,v.colorSpace,v.isVideoTexture);st(Z,v);let ht;const Bt=v.mipmaps,U=v.isVideoTexture!==!0,ot=mt.__version===void 0||j===!0,rt=$.dataReady,pt=b(v,tt);if(v.isDepthTexture)xt=S(v.format===Wi,v.type),ot&&(U?e.texStorage2D(i.TEXTURE_2D,1,xt,tt.width,tt.height):e.texImage2D(i.TEXTURE_2D,0,xt,tt.width,tt.height,0,it,_t,null));else if(v.isDataTexture)if(Bt.length>0){U&&ot&&e.texStorage2D(i.TEXTURE_2D,pt,xt,Bt[0].width,Bt[0].height);for(let et=0,Y=Bt.length;et<Y;et++)ht=Bt[et],U?rt&&e.texSubImage2D(i.TEXTURE_2D,et,0,0,ht.width,ht.height,it,_t,ht.data):e.texImage2D(i.TEXTURE_2D,et,xt,ht.width,ht.height,0,it,_t,ht.data);v.generateMipmaps=!1}else U?(ot&&e.texStorage2D(i.TEXTURE_2D,pt,xt,tt.width,tt.height),rt&&Ft(v,tt,it,_t)):e.texImage2D(i.TEXTURE_2D,0,xt,tt.width,tt.height,0,it,_t,tt.data);else if(v.isCompressedTexture)if(v.isCompressedArrayTexture){U&&ot&&e.texStorage3D(i.TEXTURE_2D_ARRAY,pt,xt,Bt[0].width,Bt[0].height,tt.depth);for(let et=0,Y=Bt.length;et<Y;et++)if(ht=Bt[et],v.format!==xn)if(it!==null)if(U){if(rt)if(v.layerUpdates.size>0){const gt=Uu(ht.width,ht.height,v.format,v.type);for(const Ct of v.layerUpdates){const se=ht.data.subarray(Ct*gt/ht.data.BYTES_PER_ELEMENT,(Ct+1)*gt/ht.data.BYTES_PER_ELEMENT);e.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,et,0,0,Ct,ht.width,ht.height,1,it,se)}v.clearLayerUpdates()}else e.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,et,0,0,0,ht.width,ht.height,tt.depth,it,ht.data)}else e.compressedTexImage3D(i.TEXTURE_2D_ARRAY,et,xt,ht.width,ht.height,tt.depth,0,ht.data,0,0);else Pt("WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else U?rt&&e.texSubImage3D(i.TEXTURE_2D_ARRAY,et,0,0,0,ht.width,ht.height,tt.depth,it,_t,ht.data):e.texImage3D(i.TEXTURE_2D_ARRAY,et,xt,ht.width,ht.height,tt.depth,0,it,_t,ht.data)}else{U&&ot&&e.texStorage2D(i.TEXTURE_2D,pt,xt,Bt[0].width,Bt[0].height);for(let et=0,Y=Bt.length;et<Y;et++)ht=Bt[et],v.format!==xn?it!==null?U?rt&&e.compressedTexSubImage2D(i.TEXTURE_2D,et,0,0,ht.width,ht.height,it,ht.data):e.compressedTexImage2D(i.TEXTURE_2D,et,xt,ht.width,ht.height,0,ht.data):Pt("WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):U?rt&&e.texSubImage2D(i.TEXTURE_2D,et,0,0,ht.width,ht.height,it,_t,ht.data):e.texImage2D(i.TEXTURE_2D,et,xt,ht.width,ht.height,0,it,_t,ht.data)}else if(v.isDataArrayTexture)if(U){if(ot&&e.texStorage3D(i.TEXTURE_2D_ARRAY,pt,xt,tt.width,tt.height,tt.depth),rt)if(v.layerUpdates.size>0){const et=Uu(tt.width,tt.height,v.format,v.type);for(const Y of v.layerUpdates){const gt=tt.data.subarray(Y*et/tt.data.BYTES_PER_ELEMENT,(Y+1)*et/tt.data.BYTES_PER_ELEMENT);e.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,Y,tt.width,tt.height,1,it,_t,gt)}v.clearLayerUpdates()}else e.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,0,tt.width,tt.height,tt.depth,it,_t,tt.data)}else e.texImage3D(i.TEXTURE_2D_ARRAY,0,xt,tt.width,tt.height,tt.depth,0,it,_t,tt.data);else if(v.isData3DTexture)U?(ot&&e.texStorage3D(i.TEXTURE_3D,pt,xt,tt.width,tt.height,tt.depth),rt&&e.texSubImage3D(i.TEXTURE_3D,0,0,0,0,tt.width,tt.height,tt.depth,it,_t,tt.data)):e.texImage3D(i.TEXTURE_3D,0,xt,tt.width,tt.height,tt.depth,0,it,_t,tt.data);else if(v.isFramebufferTexture){if(ot)if(U)e.texStorage2D(i.TEXTURE_2D,pt,xt,tt.width,tt.height);else{let et=tt.width,Y=tt.height;for(let gt=0;gt<pt;gt++)e.texImage2D(i.TEXTURE_2D,gt,xt,et,Y,0,it,_t,null),et>>=1,Y>>=1}}else if(Bt.length>0){if(U&&ot){const et=Mt(Bt[0]);e.texStorage2D(i.TEXTURE_2D,pt,xt,et.width,et.height)}for(let et=0,Y=Bt.length;et<Y;et++)ht=Bt[et],U?rt&&e.texSubImage2D(i.TEXTURE_2D,et,0,0,it,_t,ht):e.texImage2D(i.TEXTURE_2D,et,xt,it,_t,ht);v.generateMipmaps=!1}else if(U){if(ot){const et=Mt(tt);e.texStorage2D(i.TEXTURE_2D,pt,xt,et.width,et.height)}rt&&e.texSubImage2D(i.TEXTURE_2D,0,0,0,it,_t,tt)}else e.texImage2D(i.TEXTURE_2D,0,xt,it,_t,tt);p(v)&&m(Z),mt.__version=$.version,v.onUpdate&&v.onUpdate(v)}w.__version=v.version}function nt(w,v,N){if(v.image.length!==6)return;const Z=bt(w,v),j=v.source;e.bindTexture(i.TEXTURE_CUBE_MAP,w.__webglTexture,i.TEXTURE0+N);const $=n.get(j);if(j.version!==$.__version||Z===!0){e.activeTexture(i.TEXTURE0+N);const mt=Ht.getPrimaries(Ht.workingColorSpace),at=v.colorSpace===mi?null:Ht.getPrimaries(v.colorSpace),Tt=v.colorSpace===mi||mt===at?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,v.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,v.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,v.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Tt);const wt=v.isCompressedTexture||v.image[0].isCompressedTexture,tt=v.image[0]&&v.image[0].isDataTexture,it=[];for(let Y=0;Y<6;Y++)!wt&&!tt?it[Y]=g(v.image[Y],!0,r.maxCubemapSize):it[Y]=tt?v.image[Y].image:v.image[Y],it[Y]=re(v,it[Y]);const _t=it[0],xt=s.convert(v.format,v.colorSpace),ht=s.convert(v.type),Bt=T(v.internalFormat,xt,ht,v.colorSpace),U=v.isVideoTexture!==!0,ot=$.__version===void 0||Z===!0,rt=j.dataReady;let pt=b(v,_t);st(i.TEXTURE_CUBE_MAP,v);let et;if(wt){U&&ot&&e.texStorage2D(i.TEXTURE_CUBE_MAP,pt,Bt,_t.width,_t.height);for(let Y=0;Y<6;Y++){et=it[Y].mipmaps;for(let gt=0;gt<et.length;gt++){const Ct=et[gt];v.format!==xn?xt!==null?U?rt&&e.compressedTexSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+Y,gt,0,0,Ct.width,Ct.height,xt,Ct.data):e.compressedTexImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+Y,gt,Bt,Ct.width,Ct.height,0,Ct.data):Pt("WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):U?rt&&e.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+Y,gt,0,0,Ct.width,Ct.height,xt,ht,Ct.data):e.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+Y,gt,Bt,Ct.width,Ct.height,0,xt,ht,Ct.data)}}}else{if(et=v.mipmaps,U&&ot){et.length>0&&pt++;const Y=Mt(it[0]);e.texStorage2D(i.TEXTURE_CUBE_MAP,pt,Bt,Y.width,Y.height)}for(let Y=0;Y<6;Y++)if(tt){U?rt&&e.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+Y,0,0,0,it[Y].width,it[Y].height,xt,ht,it[Y].data):e.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+Y,0,Bt,it[Y].width,it[Y].height,0,xt,ht,it[Y].data);for(let gt=0;gt<et.length;gt++){const se=et[gt].image[Y].image;U?rt&&e.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+Y,gt+1,0,0,se.width,se.height,xt,ht,se.data):e.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+Y,gt+1,Bt,se.width,se.height,0,xt,ht,se.data)}}else{U?rt&&e.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+Y,0,0,0,xt,ht,it[Y]):e.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+Y,0,Bt,xt,ht,it[Y]);for(let gt=0;gt<et.length;gt++){const Ct=et[gt];U?rt&&e.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+Y,gt+1,0,0,xt,ht,Ct.image[Y]):e.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+Y,gt+1,Bt,xt,ht,Ct.image[Y])}}}p(v)&&m(i.TEXTURE_CUBE_MAP),$.__version=j.version,v.onUpdate&&v.onUpdate(v)}w.__version=v.version}function lt(w,v,N,Z,j,$){const mt=s.convert(N.format,N.colorSpace),at=s.convert(N.type),Tt=T(N.internalFormat,mt,at,N.colorSpace),wt=n.get(v),tt=n.get(N);if(tt.__renderTarget=v,!wt.__hasExternalTextures){const it=Math.max(1,v.width>>$),_t=Math.max(1,v.height>>$);j===i.TEXTURE_3D||j===i.TEXTURE_2D_ARRAY?e.texImage3D(j,$,Tt,it,_t,v.depth,0,mt,at,null):e.texImage2D(j,$,Tt,it,_t,0,mt,at,null)}e.bindFramebuffer(i.FRAMEBUFFER,w),_e(v)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,Z,j,tt.__webglTexture,0,I(v)):(j===i.TEXTURE_2D||j>=i.TEXTURE_CUBE_MAP_POSITIVE_X&&j<=i.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&i.framebufferTexture2D(i.FRAMEBUFFER,Z,j,tt.__webglTexture,$),e.bindFramebuffer(i.FRAMEBUFFER,null)}function Lt(w,v,N){if(i.bindRenderbuffer(i.RENDERBUFFER,w),v.depthBuffer){const Z=v.depthTexture,j=Z&&Z.isDepthTexture?Z.type:null,$=S(v.stencilBuffer,j),mt=v.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;_e(v)?o.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,I(v),$,v.width,v.height):N?i.renderbufferStorageMultisample(i.RENDERBUFFER,I(v),$,v.width,v.height):i.renderbufferStorage(i.RENDERBUFFER,$,v.width,v.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,mt,i.RENDERBUFFER,w)}else{const Z=v.textures;for(let j=0;j<Z.length;j++){const $=Z[j],mt=s.convert($.format,$.colorSpace),at=s.convert($.type),Tt=T($.internalFormat,mt,at,$.colorSpace);_e(v)?o.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,I(v),Tt,v.width,v.height):N?i.renderbufferStorageMultisample(i.RENDERBUFFER,I(v),Tt,v.width,v.height):i.renderbufferStorage(i.RENDERBUFFER,Tt,v.width,v.height)}}i.bindRenderbuffer(i.RENDERBUFFER,null)}function At(w,v,N){const Z=v.isWebGLCubeRenderTarget===!0;if(e.bindFramebuffer(i.FRAMEBUFFER,w),!(v.depthTexture&&v.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const j=n.get(v.depthTexture);if(j.__renderTarget=v,(!j.__webglTexture||v.depthTexture.image.width!==v.width||v.depthTexture.image.height!==v.height)&&(v.depthTexture.image.width=v.width,v.depthTexture.image.height=v.height,v.depthTexture.needsUpdate=!0),Z){if(j.__webglInit===void 0&&(j.__webglInit=!0,v.depthTexture.addEventListener("dispose",A)),j.__webglTexture===void 0){j.__webglTexture=i.createTexture(),e.bindTexture(i.TEXTURE_CUBE_MAP,j.__webglTexture),st(i.TEXTURE_CUBE_MAP,v.depthTexture);const wt=s.convert(v.depthTexture.format),tt=s.convert(v.depthTexture.type);let it;v.depthTexture.format===ni?it=i.DEPTH_COMPONENT24:v.depthTexture.format===Wi&&(it=i.DEPTH24_STENCIL8);for(let _t=0;_t<6;_t++)i.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+_t,0,it,v.width,v.height,0,wt,tt,null)}}else C(v.depthTexture,0);const $=j.__webglTexture,mt=I(v),at=Z?i.TEXTURE_CUBE_MAP_POSITIVE_X+N:i.TEXTURE_2D,Tt=v.depthTexture.format===Wi?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;if(v.depthTexture.format===ni)_e(v)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,Tt,at,$,0,mt):i.framebufferTexture2D(i.FRAMEBUFFER,Tt,at,$,0);else if(v.depthTexture.format===Wi)_e(v)?o.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,Tt,at,$,0,mt):i.framebufferTexture2D(i.FRAMEBUFFER,Tt,at,$,0);else throw new Error("Unknown depthTexture format")}function Rt(w){const v=n.get(w),N=w.isWebGLCubeRenderTarget===!0;if(v.__boundDepthTexture!==w.depthTexture){const Z=w.depthTexture;if(v.__depthDisposeCallback&&v.__depthDisposeCallback(),Z){const j=()=>{delete v.__boundDepthTexture,delete v.__depthDisposeCallback,Z.removeEventListener("dispose",j)};Z.addEventListener("dispose",j),v.__depthDisposeCallback=j}v.__boundDepthTexture=Z}if(w.depthTexture&&!v.__autoAllocateDepthBuffer)if(N)for(let Z=0;Z<6;Z++)At(v.__webglFramebuffer[Z],w,Z);else{const Z=w.texture.mipmaps;Z&&Z.length>0?At(v.__webglFramebuffer[0],w,0):At(v.__webglFramebuffer,w,0)}else if(N){v.__webglDepthbuffer=[];for(let Z=0;Z<6;Z++)if(e.bindFramebuffer(i.FRAMEBUFFER,v.__webglFramebuffer[Z]),v.__webglDepthbuffer[Z]===void 0)v.__webglDepthbuffer[Z]=i.createRenderbuffer(),Lt(v.__webglDepthbuffer[Z],w,!1);else{const j=w.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,$=v.__webglDepthbuffer[Z];i.bindRenderbuffer(i.RENDERBUFFER,$),i.framebufferRenderbuffer(i.FRAMEBUFFER,j,i.RENDERBUFFER,$)}}else{const Z=w.texture.mipmaps;if(Z&&Z.length>0?e.bindFramebuffer(i.FRAMEBUFFER,v.__webglFramebuffer[0]):e.bindFramebuffer(i.FRAMEBUFFER,v.__webglFramebuffer),v.__webglDepthbuffer===void 0)v.__webglDepthbuffer=i.createRenderbuffer(),Lt(v.__webglDepthbuffer,w,!1);else{const j=w.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,$=v.__webglDepthbuffer;i.bindRenderbuffer(i.RENDERBUFFER,$),i.framebufferRenderbuffer(i.FRAMEBUFFER,j,i.RENDERBUFFER,$)}}e.bindFramebuffer(i.FRAMEBUFFER,null)}function ye(w,v,N){const Z=n.get(w);v!==void 0&&lt(Z.__webglFramebuffer,w,w.texture,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,0),N!==void 0&&Rt(w)}function Gt(w){const v=w.texture,N=n.get(w),Z=n.get(v);w.addEventListener("dispose",R);const j=w.textures,$=w.isWebGLCubeRenderTarget===!0,mt=j.length>1;if(mt||(Z.__webglTexture===void 0&&(Z.__webglTexture=i.createTexture()),Z.__version=v.version,a.memory.textures++),$){N.__webglFramebuffer=[];for(let at=0;at<6;at++)if(v.mipmaps&&v.mipmaps.length>0){N.__webglFramebuffer[at]=[];for(let Tt=0;Tt<v.mipmaps.length;Tt++)N.__webglFramebuffer[at][Tt]=i.createFramebuffer()}else N.__webglFramebuffer[at]=i.createFramebuffer()}else{if(v.mipmaps&&v.mipmaps.length>0){N.__webglFramebuffer=[];for(let at=0;at<v.mipmaps.length;at++)N.__webglFramebuffer[at]=i.createFramebuffer()}else N.__webglFramebuffer=i.createFramebuffer();if(mt)for(let at=0,Tt=j.length;at<Tt;at++){const wt=n.get(j[at]);wt.__webglTexture===void 0&&(wt.__webglTexture=i.createTexture(),a.memory.textures++)}if(w.samples>0&&_e(w)===!1){N.__webglMultisampledFramebuffer=i.createFramebuffer(),N.__webglColorRenderbuffer=[],e.bindFramebuffer(i.FRAMEBUFFER,N.__webglMultisampledFramebuffer);for(let at=0;at<j.length;at++){const Tt=j[at];N.__webglColorRenderbuffer[at]=i.createRenderbuffer(),i.bindRenderbuffer(i.RENDERBUFFER,N.__webglColorRenderbuffer[at]);const wt=s.convert(Tt.format,Tt.colorSpace),tt=s.convert(Tt.type),it=T(Tt.internalFormat,wt,tt,Tt.colorSpace,w.isXRRenderTarget===!0),_t=I(w);i.renderbufferStorageMultisample(i.RENDERBUFFER,_t,it,w.width,w.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+at,i.RENDERBUFFER,N.__webglColorRenderbuffer[at])}i.bindRenderbuffer(i.RENDERBUFFER,null),w.depthBuffer&&(N.__webglDepthRenderbuffer=i.createRenderbuffer(),Lt(N.__webglDepthRenderbuffer,w,!0)),e.bindFramebuffer(i.FRAMEBUFFER,null)}}if($){e.bindTexture(i.TEXTURE_CUBE_MAP,Z.__webglTexture),st(i.TEXTURE_CUBE_MAP,v);for(let at=0;at<6;at++)if(v.mipmaps&&v.mipmaps.length>0)for(let Tt=0;Tt<v.mipmaps.length;Tt++)lt(N.__webglFramebuffer[at][Tt],w,v,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+at,Tt);else lt(N.__webglFramebuffer[at],w,v,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+at,0);p(v)&&m(i.TEXTURE_CUBE_MAP),e.unbindTexture()}else if(mt){for(let at=0,Tt=j.length;at<Tt;at++){const wt=j[at],tt=n.get(wt);let it=i.TEXTURE_2D;(w.isWebGL3DRenderTarget||w.isWebGLArrayRenderTarget)&&(it=w.isWebGL3DRenderTarget?i.TEXTURE_3D:i.TEXTURE_2D_ARRAY),e.bindTexture(it,tt.__webglTexture),st(it,wt),lt(N.__webglFramebuffer,w,wt,i.COLOR_ATTACHMENT0+at,it,0),p(wt)&&m(it)}e.unbindTexture()}else{let at=i.TEXTURE_2D;if((w.isWebGL3DRenderTarget||w.isWebGLArrayRenderTarget)&&(at=w.isWebGL3DRenderTarget?i.TEXTURE_3D:i.TEXTURE_2D_ARRAY),e.bindTexture(at,Z.__webglTexture),st(at,v),v.mipmaps&&v.mipmaps.length>0)for(let Tt=0;Tt<v.mipmaps.length;Tt++)lt(N.__webglFramebuffer[Tt],w,v,i.COLOR_ATTACHMENT0,at,Tt);else lt(N.__webglFramebuffer,w,v,i.COLOR_ATTACHMENT0,at,0);p(v)&&m(at),e.unbindTexture()}w.depthBuffer&&Rt(w)}function Yt(w){const v=w.textures;for(let N=0,Z=v.length;N<Z;N++){const j=v[N];if(p(j)){const $=M(w),mt=n.get(j).__webglTexture;e.bindTexture($,mt),m($),e.unbindTexture()}}}const te=[],Ot=[];function he(w){if(w.samples>0){if(_e(w)===!1){const v=w.textures,N=w.width,Z=w.height;let j=i.COLOR_BUFFER_BIT;const $=w.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,mt=n.get(w),at=v.length>1;if(at)for(let wt=0;wt<v.length;wt++)e.bindFramebuffer(i.FRAMEBUFFER,mt.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+wt,i.RENDERBUFFER,null),e.bindFramebuffer(i.FRAMEBUFFER,mt.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+wt,i.TEXTURE_2D,null,0);e.bindFramebuffer(i.READ_FRAMEBUFFER,mt.__webglMultisampledFramebuffer);const Tt=w.texture.mipmaps;Tt&&Tt.length>0?e.bindFramebuffer(i.DRAW_FRAMEBUFFER,mt.__webglFramebuffer[0]):e.bindFramebuffer(i.DRAW_FRAMEBUFFER,mt.__webglFramebuffer);for(let wt=0;wt<v.length;wt++){if(w.resolveDepthBuffer&&(w.depthBuffer&&(j|=i.DEPTH_BUFFER_BIT),w.stencilBuffer&&w.resolveStencilBuffer&&(j|=i.STENCIL_BUFFER_BIT)),at){i.framebufferRenderbuffer(i.READ_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.RENDERBUFFER,mt.__webglColorRenderbuffer[wt]);const tt=n.get(v[wt]).__webglTexture;i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,tt,0)}i.blitFramebuffer(0,0,N,Z,0,0,N,Z,j,i.NEAREST),l===!0&&(te.length=0,Ot.length=0,te.push(i.COLOR_ATTACHMENT0+wt),w.depthBuffer&&w.resolveDepthBuffer===!1&&(te.push($),Ot.push($),i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,Ot)),i.invalidateFramebuffer(i.READ_FRAMEBUFFER,te))}if(e.bindFramebuffer(i.READ_FRAMEBUFFER,null),e.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),at)for(let wt=0;wt<v.length;wt++){e.bindFramebuffer(i.FRAMEBUFFER,mt.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+wt,i.RENDERBUFFER,mt.__webglColorRenderbuffer[wt]);const tt=n.get(v[wt]).__webglTexture;e.bindFramebuffer(i.FRAMEBUFFER,mt.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+wt,i.TEXTURE_2D,tt,0)}e.bindFramebuffer(i.DRAW_FRAMEBUFFER,mt.__webglMultisampledFramebuffer)}else if(w.depthBuffer&&w.resolveDepthBuffer===!1&&l){const v=w.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,[v])}}}function I(w){return Math.min(r.maxSamples,w.samples)}function _e(w){const v=n.get(w);return w.samples>0&&t.has("WEBGL_multisampled_render_to_texture")===!0&&v.__useRenderToTexture!==!1}function qt(w){const v=a.render.frame;u.get(w)!==v&&(u.set(w,v),w.update())}function re(w,v){const N=w.colorSpace,Z=w.format,j=w.type;return w.isCompressedTexture===!0||w.isVideoTexture===!0||N!==Ur&&N!==mi&&(Ht.getTransfer(N)===Kt?(Z!==xn||j!==cn)&&Pt("WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):Xt("WebGLTextures: Unsupported texture color space:",N)),v}function Mt(w){return typeof HTMLImageElement<"u"&&w instanceof HTMLImageElement?(c.width=w.naturalWidth||w.width,c.height=w.naturalHeight||w.height):typeof VideoFrame<"u"&&w instanceof VideoFrame?(c.width=w.displayWidth,c.height=w.displayHeight):(c.width=w.width,c.height=w.height),c}this.allocateTextureUnit=k,this.resetTextureUnits=B,this.setTexture2D=C,this.setTexture2DArray=L,this.setTexture3D=P,this.setTextureCube=z,this.rebindTextures=ye,this.setupRenderTarget=Gt,this.updateRenderTargetMipmap=Yt,this.updateMultisampleRenderTarget=he,this.setupDepthRenderbuffer=Rt,this.setupFrameBufferTexture=lt,this.useMultisampledRTT=_e,this.isReversedDepthBuffer=function(){return e.buffers.depth.getReversed()}}function rM(i,t){function e(n,r=mi){let s;const a=Ht.getTransfer(r);if(n===cn)return i.UNSIGNED_BYTE;if(n===Mc)return i.UNSIGNED_SHORT_4_4_4_4;if(n===Sc)return i.UNSIGNED_SHORT_5_5_5_1;if(n===Fh)return i.UNSIGNED_INT_5_9_9_9_REV;if(n===Oh)return i.UNSIGNED_INT_10F_11F_11F_REV;if(n===Uh)return i.BYTE;if(n===Nh)return i.SHORT;if(n===ps)return i.UNSIGNED_SHORT;if(n===vc)return i.INT;if(n===Un)return i.UNSIGNED_INT;if(n===wn)return i.FLOAT;if(n===ei)return i.HALF_FLOAT;if(n===Bh)return i.ALPHA;if(n===kh)return i.RGB;if(n===xn)return i.RGBA;if(n===ni)return i.DEPTH_COMPONENT;if(n===Wi)return i.DEPTH_STENCIL;if(n===zh)return i.RED;if(n===yc)return i.RED_INTEGER;if(n===Ir)return i.RG;if(n===Ec)return i.RG_INTEGER;if(n===Tc)return i.RGBA_INTEGER;if(n===la||n===ca||n===ua||n===fa)if(a===Kt)if(s=t.get("WEBGL_compressed_texture_s3tc_srgb"),s!==null){if(n===la)return s.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===ca)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===ua)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===fa)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(s=t.get("WEBGL_compressed_texture_s3tc"),s!==null){if(n===la)return s.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===ca)return s.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===ua)return s.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===fa)return s.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===cl||n===ul||n===fl||n===hl)if(s=t.get("WEBGL_compressed_texture_pvrtc"),s!==null){if(n===cl)return s.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===ul)return s.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===fl)return s.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===hl)return s.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===dl||n===pl||n===ml||n===_l||n===gl||n===xl||n===vl)if(s=t.get("WEBGL_compressed_texture_etc"),s!==null){if(n===dl||n===pl)return a===Kt?s.COMPRESSED_SRGB8_ETC2:s.COMPRESSED_RGB8_ETC2;if(n===ml)return a===Kt?s.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:s.COMPRESSED_RGBA8_ETC2_EAC;if(n===_l)return s.COMPRESSED_R11_EAC;if(n===gl)return s.COMPRESSED_SIGNED_R11_EAC;if(n===xl)return s.COMPRESSED_RG11_EAC;if(n===vl)return s.COMPRESSED_SIGNED_RG11_EAC}else return null;if(n===Ml||n===Sl||n===yl||n===El||n===Tl||n===bl||n===Al||n===wl||n===Rl||n===Cl||n===Pl||n===Dl||n===Ll||n===Il)if(s=t.get("WEBGL_compressed_texture_astc"),s!==null){if(n===Ml)return a===Kt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:s.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===Sl)return a===Kt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:s.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===yl)return a===Kt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:s.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===El)return a===Kt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:s.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===Tl)return a===Kt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:s.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===bl)return a===Kt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:s.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===Al)return a===Kt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:s.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===wl)return a===Kt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:s.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===Rl)return a===Kt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:s.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===Cl)return a===Kt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:s.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===Pl)return a===Kt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:s.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===Dl)return a===Kt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:s.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===Ll)return a===Kt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:s.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===Il)return a===Kt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:s.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===Ul||n===Nl||n===Fl)if(s=t.get("EXT_texture_compression_bptc"),s!==null){if(n===Ul)return a===Kt?s.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:s.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===Nl)return s.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===Fl)return s.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===Ol||n===Bl||n===kl||n===zl)if(s=t.get("EXT_texture_compression_rgtc"),s!==null){if(n===Ol)return s.COMPRESSED_RED_RGTC1_EXT;if(n===Bl)return s.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===kl)return s.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===zl)return s.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===ms?i.UNSIGNED_INT_24_8:i[n]!==void 0?i[n]:null}return{convert:e}}const sM=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,aM=`
uniform sampler2DArray depthColor;
uniform float depthWidth;
uniform float depthHeight;

void main() {

	vec2 coord = vec2( gl_FragCoord.x / depthWidth, gl_FragCoord.y / depthHeight );

	if ( coord.x >= 1.0 ) {

		gl_FragDepth = texture( depthColor, vec3( coord.x - 1.0, coord.y, 1 ) ).r;

	} else {

		gl_FragDepth = texture( depthColor, vec3( coord.x, coord.y, 0 ) ).r;

	}

}`;class oM{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(t,e){if(this.texture===null){const n=new Kh(t.texture);(t.depthNear!==e.depthNear||t.depthFar!==e.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=n}}getMesh(t){if(this.texture!==null&&this.mesh===null){const e=t.cameras[0].viewport,n=new Fn({vertexShader:sM,fragmentShader:aM,uniforms:{depthColor:{value:this.texture},depthWidth:{value:e.z},depthHeight:{value:e.w}}});this.mesh=new Nn(new bs(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class lM extends Br{constructor(t,e){super();const n=this;let r=null,s=1,a=null,o="local-floor",l=1,c=null,u=null,h=null,f=null,d=null,_=null;const g=typeof XRWebGLBinding<"u",p=new oM,m={},M=e.getContextAttributes();let T=null,S=null;const b=[],A=[],R=new Qt;let x=null;const y=new ln;y.viewport=new me;const G=new ln;G.viewport=new me;const D=[y,G],B=new M_;let k=null,X=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(K){let nt=b[K];return nt===void 0&&(nt=new uo,b[K]=nt),nt.getTargetRaySpace()},this.getControllerGrip=function(K){let nt=b[K];return nt===void 0&&(nt=new uo,b[K]=nt),nt.getGripSpace()},this.getHand=function(K){let nt=b[K];return nt===void 0&&(nt=new uo,b[K]=nt),nt.getHandSpace()};function C(K){const nt=A.indexOf(K.inputSource);if(nt===-1)return;const lt=b[nt];lt!==void 0&&(lt.update(K.inputSource,K.frame,c||a),lt.dispatchEvent({type:K.type,data:K.inputSource}))}function L(){r.removeEventListener("select",C),r.removeEventListener("selectstart",C),r.removeEventListener("selectend",C),r.removeEventListener("squeeze",C),r.removeEventListener("squeezestart",C),r.removeEventListener("squeezeend",C),r.removeEventListener("end",L),r.removeEventListener("inputsourceschange",P);for(let K=0;K<b.length;K++){const nt=A[K];nt!==null&&(A[K]=null,b[K].disconnect(nt))}k=null,X=null,p.reset();for(const K in m)delete m[K];t.setRenderTarget(T),d=null,f=null,h=null,r=null,S=null,Ft.stop(),n.isPresenting=!1,t.setPixelRatio(x),t.setSize(R.width,R.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(K){s=K,n.isPresenting===!0&&Pt("WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(K){o=K,n.isPresenting===!0&&Pt("WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return c||a},this.setReferenceSpace=function(K){c=K},this.getBaseLayer=function(){return f!==null?f:d},this.getBinding=function(){return h===null&&g&&(h=new XRWebGLBinding(r,e)),h},this.getFrame=function(){return _},this.getSession=function(){return r},this.setSession=async function(K){if(r=K,r!==null){if(T=t.getRenderTarget(),r.addEventListener("select",C),r.addEventListener("selectstart",C),r.addEventListener("selectend",C),r.addEventListener("squeeze",C),r.addEventListener("squeezestart",C),r.addEventListener("squeezeend",C),r.addEventListener("end",L),r.addEventListener("inputsourceschange",P),M.xrCompatible!==!0&&await e.makeXRCompatible(),x=t.getPixelRatio(),t.getSize(R),g&&"createProjectionLayer"in XRWebGLBinding.prototype){let lt=null,Lt=null,At=null;M.depth&&(At=M.stencil?e.DEPTH24_STENCIL8:e.DEPTH_COMPONENT24,lt=M.stencil?Wi:ni,Lt=M.stencil?ms:Un);const Rt={colorFormat:e.RGBA8,depthFormat:At,scaleFactor:s};h=this.getBinding(),f=h.createProjectionLayer(Rt),r.updateRenderState({layers:[f]}),t.setPixelRatio(1),t.setSize(f.textureWidth,f.textureHeight,!1),S=new Pn(f.textureWidth,f.textureHeight,{format:xn,type:cn,depthTexture:new _s(f.textureWidth,f.textureHeight,Lt,void 0,void 0,void 0,void 0,void 0,void 0,lt),stencilBuffer:M.stencil,colorSpace:t.outputColorSpace,samples:M.antialias?4:0,resolveDepthBuffer:f.ignoreDepthValues===!1,resolveStencilBuffer:f.ignoreDepthValues===!1})}else{const lt={antialias:M.antialias,alpha:!0,depth:M.depth,stencil:M.stencil,framebufferScaleFactor:s};d=new XRWebGLLayer(r,e,lt),r.updateRenderState({baseLayer:d}),t.setPixelRatio(1),t.setSize(d.framebufferWidth,d.framebufferHeight,!1),S=new Pn(d.framebufferWidth,d.framebufferHeight,{format:xn,type:cn,colorSpace:t.outputColorSpace,stencilBuffer:M.stencil,resolveDepthBuffer:d.ignoreDepthValues===!1,resolveStencilBuffer:d.ignoreDepthValues===!1})}S.isXRRenderTarget=!0,this.setFoveation(l),c=null,a=await r.requestReferenceSpace(o),Ft.setContext(r),Ft.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(r!==null)return r.environmentBlendMode},this.getDepthTexture=function(){return p.getDepthTexture()};function P(K){for(let nt=0;nt<K.removed.length;nt++){const lt=K.removed[nt],Lt=A.indexOf(lt);Lt>=0&&(A[Lt]=null,b[Lt].disconnect(lt))}for(let nt=0;nt<K.added.length;nt++){const lt=K.added[nt];let Lt=A.indexOf(lt);if(Lt===-1){for(let Rt=0;Rt<b.length;Rt++)if(Rt>=A.length){A.push(lt),Lt=Rt;break}else if(A[Rt]===null){A[Rt]=lt,Lt=Rt;break}if(Lt===-1)break}const At=b[Lt];At&&At.connect(lt)}}const z=new W,O=new W;function J(K,nt,lt){z.setFromMatrixPosition(nt.matrixWorld),O.setFromMatrixPosition(lt.matrixWorld);const Lt=z.distanceTo(O),At=nt.projectionMatrix.elements,Rt=lt.projectionMatrix.elements,ye=At[14]/(At[10]-1),Gt=At[14]/(At[10]+1),Yt=(At[9]+1)/At[5],te=(At[9]-1)/At[5],Ot=(At[8]-1)/At[0],he=(Rt[8]+1)/Rt[0],I=ye*Ot,_e=ye*he,qt=Lt/(-Ot+he),re=qt*-Ot;if(nt.matrixWorld.decompose(K.position,K.quaternion,K.scale),K.translateX(re),K.translateZ(qt),K.matrixWorld.compose(K.position,K.quaternion,K.scale),K.matrixWorldInverse.copy(K.matrixWorld).invert(),At[10]===-1)K.projectionMatrix.copy(nt.projectionMatrix),K.projectionMatrixInverse.copy(nt.projectionMatrixInverse);else{const Mt=ye+qt,w=Gt+qt,v=I-re,N=_e+(Lt-re),Z=Yt*Gt/w*Mt,j=te*Gt/w*Mt;K.projectionMatrix.makePerspective(v,N,Z,j,Mt,w),K.projectionMatrixInverse.copy(K.projectionMatrix).invert()}}function Q(K,nt){nt===null?K.matrixWorld.copy(K.matrix):K.matrixWorld.multiplyMatrices(nt.matrixWorld,K.matrix),K.matrixWorldInverse.copy(K.matrixWorld).invert()}this.updateCamera=function(K){if(r===null)return;let nt=K.near,lt=K.far;p.texture!==null&&(p.depthNear>0&&(nt=p.depthNear),p.depthFar>0&&(lt=p.depthFar)),B.near=G.near=y.near=nt,B.far=G.far=y.far=lt,(k!==B.near||X!==B.far)&&(r.updateRenderState({depthNear:B.near,depthFar:B.far}),k=B.near,X=B.far),B.layers.mask=K.layers.mask|6,y.layers.mask=B.layers.mask&-5,G.layers.mask=B.layers.mask&-3;const Lt=K.parent,At=B.cameras;Q(B,Lt);for(let Rt=0;Rt<At.length;Rt++)Q(At[Rt],Lt);At.length===2?J(B,y,G):B.projectionMatrix.copy(y.projectionMatrix),st(K,B,Lt)};function st(K,nt,lt){lt===null?K.matrix.copy(nt.matrixWorld):(K.matrix.copy(lt.matrixWorld),K.matrix.invert(),K.matrix.multiply(nt.matrixWorld)),K.matrix.decompose(K.position,K.quaternion,K.scale),K.updateMatrixWorld(!0),K.projectionMatrix.copy(nt.projectionMatrix),K.projectionMatrixInverse.copy(nt.projectionMatrixInverse),K.isPerspectiveCamera&&(K.fov=Vl*2*Math.atan(1/K.projectionMatrix.elements[5]),K.zoom=1)}this.getCamera=function(){return B},this.getFoveation=function(){if(!(f===null&&d===null))return l},this.setFoveation=function(K){l=K,f!==null&&(f.fixedFoveation=K),d!==null&&d.fixedFoveation!==void 0&&(d.fixedFoveation=K)},this.hasDepthSensing=function(){return p.texture!==null},this.getDepthSensingMesh=function(){return p.getMesh(B)},this.getCameraTexture=function(K){return m[K]};let bt=null;function Ut(K,nt){if(u=nt.getViewerPose(c||a),_=nt,u!==null){const lt=u.views;d!==null&&(t.setRenderTargetFramebuffer(S,d.framebuffer),t.setRenderTarget(S));let Lt=!1;lt.length!==B.cameras.length&&(B.cameras.length=0,Lt=!0);for(let Gt=0;Gt<lt.length;Gt++){const Yt=lt[Gt];let te=null;if(d!==null)te=d.getViewport(Yt);else{const he=h.getViewSubImage(f,Yt);te=he.viewport,Gt===0&&(t.setRenderTargetTextures(S,he.colorTexture,he.depthStencilTexture),t.setRenderTarget(S))}let Ot=D[Gt];Ot===void 0&&(Ot=new ln,Ot.layers.enable(Gt),Ot.viewport=new me,D[Gt]=Ot),Ot.matrix.fromArray(Yt.transform.matrix),Ot.matrix.decompose(Ot.position,Ot.quaternion,Ot.scale),Ot.projectionMatrix.fromArray(Yt.projectionMatrix),Ot.projectionMatrixInverse.copy(Ot.projectionMatrix).invert(),Ot.viewport.set(te.x,te.y,te.width,te.height),Gt===0&&(B.matrix.copy(Ot.matrix),B.matrix.decompose(B.position,B.quaternion,B.scale)),Lt===!0&&B.cameras.push(Ot)}const At=r.enabledFeatures;if(At&&At.includes("depth-sensing")&&r.depthUsage=="gpu-optimized"&&g){h=n.getBinding();const Gt=h.getDepthInformation(lt[0]);Gt&&Gt.isValid&&Gt.texture&&p.init(Gt,r.renderState)}if(At&&At.includes("camera-access")&&g){t.state.unbindTexture(),h=n.getBinding();for(let Gt=0;Gt<lt.length;Gt++){const Yt=lt[Gt].camera;if(Yt){let te=m[Yt];te||(te=new Kh,m[Yt]=te);const Ot=h.getCameraImage(Yt);te.sourceTexture=Ot}}}}for(let lt=0;lt<b.length;lt++){const Lt=A[lt],At=b[lt];Lt!==null&&At!==void 0&&At.update(Lt,nt,c||a)}bt&&bt(K,nt),nt.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:nt}),_=null}const Ft=new Qh;Ft.setAnimationLoop(Ut),this.setAnimationLoop=function(K){bt=K},this.dispose=function(){}}}const Fi=new ii,cM=new ve;function uM(i,t){function e(p,m){p.matrixAutoUpdate===!0&&p.updateMatrix(),m.value.copy(p.matrix)}function n(p,m){m.color.getRGB(p.fogColor.value,Zh(i)),m.isFog?(p.fogNear.value=m.near,p.fogFar.value=m.far):m.isFogExp2&&(p.fogDensity.value=m.density)}function r(p,m,M,T,S){m.isMeshBasicMaterial?s(p,m):m.isMeshLambertMaterial?(s(p,m),m.envMap&&(p.envMapIntensity.value=m.envMapIntensity)):m.isMeshToonMaterial?(s(p,m),h(p,m)):m.isMeshPhongMaterial?(s(p,m),u(p,m),m.envMap&&(p.envMapIntensity.value=m.envMapIntensity)):m.isMeshStandardMaterial?(s(p,m),f(p,m),m.isMeshPhysicalMaterial&&d(p,m,S)):m.isMeshMatcapMaterial?(s(p,m),_(p,m)):m.isMeshDepthMaterial?s(p,m):m.isMeshDistanceMaterial?(s(p,m),g(p,m)):m.isMeshNormalMaterial?s(p,m):m.isLineBasicMaterial?(a(p,m),m.isLineDashedMaterial&&o(p,m)):m.isPointsMaterial?l(p,m,M,T):m.isSpriteMaterial?c(p,m):m.isShadowMaterial?(p.color.value.copy(m.color),p.opacity.value=m.opacity):m.isShaderMaterial&&(m.uniformsNeedUpdate=!1)}function s(p,m){p.opacity.value=m.opacity,m.color&&p.diffuse.value.copy(m.color),m.emissive&&p.emissive.value.copy(m.emissive).multiplyScalar(m.emissiveIntensity),m.map&&(p.map.value=m.map,e(m.map,p.mapTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,e(m.alphaMap,p.alphaMapTransform)),m.bumpMap&&(p.bumpMap.value=m.bumpMap,e(m.bumpMap,p.bumpMapTransform),p.bumpScale.value=m.bumpScale,m.side===We&&(p.bumpScale.value*=-1)),m.normalMap&&(p.normalMap.value=m.normalMap,e(m.normalMap,p.normalMapTransform),p.normalScale.value.copy(m.normalScale),m.side===We&&p.normalScale.value.negate()),m.displacementMap&&(p.displacementMap.value=m.displacementMap,e(m.displacementMap,p.displacementMapTransform),p.displacementScale.value=m.displacementScale,p.displacementBias.value=m.displacementBias),m.emissiveMap&&(p.emissiveMap.value=m.emissiveMap,e(m.emissiveMap,p.emissiveMapTransform)),m.specularMap&&(p.specularMap.value=m.specularMap,e(m.specularMap,p.specularMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest);const M=t.get(m),T=M.envMap,S=M.envMapRotation;T&&(p.envMap.value=T,Fi.copy(S),Fi.x*=-1,Fi.y*=-1,Fi.z*=-1,T.isCubeTexture&&T.isRenderTargetTexture===!1&&(Fi.y*=-1,Fi.z*=-1),p.envMapRotation.value.setFromMatrix4(cM.makeRotationFromEuler(Fi)),p.flipEnvMap.value=T.isCubeTexture&&T.isRenderTargetTexture===!1?-1:1,p.reflectivity.value=m.reflectivity,p.ior.value=m.ior,p.refractionRatio.value=m.refractionRatio),m.lightMap&&(p.lightMap.value=m.lightMap,p.lightMapIntensity.value=m.lightMapIntensity,e(m.lightMap,p.lightMapTransform)),m.aoMap&&(p.aoMap.value=m.aoMap,p.aoMapIntensity.value=m.aoMapIntensity,e(m.aoMap,p.aoMapTransform))}function a(p,m){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,m.map&&(p.map.value=m.map,e(m.map,p.mapTransform))}function o(p,m){p.dashSize.value=m.dashSize,p.totalSize.value=m.dashSize+m.gapSize,p.scale.value=m.scale}function l(p,m,M,T){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,p.size.value=m.size*M,p.scale.value=T*.5,m.map&&(p.map.value=m.map,e(m.map,p.uvTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,e(m.alphaMap,p.alphaMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest)}function c(p,m){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,p.rotation.value=m.rotation,m.map&&(p.map.value=m.map,e(m.map,p.mapTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,e(m.alphaMap,p.alphaMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest)}function u(p,m){p.specular.value.copy(m.specular),p.shininess.value=Math.max(m.shininess,1e-4)}function h(p,m){m.gradientMap&&(p.gradientMap.value=m.gradientMap)}function f(p,m){p.metalness.value=m.metalness,m.metalnessMap&&(p.metalnessMap.value=m.metalnessMap,e(m.metalnessMap,p.metalnessMapTransform)),p.roughness.value=m.roughness,m.roughnessMap&&(p.roughnessMap.value=m.roughnessMap,e(m.roughnessMap,p.roughnessMapTransform)),m.envMap&&(p.envMapIntensity.value=m.envMapIntensity)}function d(p,m,M){p.ior.value=m.ior,m.sheen>0&&(p.sheenColor.value.copy(m.sheenColor).multiplyScalar(m.sheen),p.sheenRoughness.value=m.sheenRoughness,m.sheenColorMap&&(p.sheenColorMap.value=m.sheenColorMap,e(m.sheenColorMap,p.sheenColorMapTransform)),m.sheenRoughnessMap&&(p.sheenRoughnessMap.value=m.sheenRoughnessMap,e(m.sheenRoughnessMap,p.sheenRoughnessMapTransform))),m.clearcoat>0&&(p.clearcoat.value=m.clearcoat,p.clearcoatRoughness.value=m.clearcoatRoughness,m.clearcoatMap&&(p.clearcoatMap.value=m.clearcoatMap,e(m.clearcoatMap,p.clearcoatMapTransform)),m.clearcoatRoughnessMap&&(p.clearcoatRoughnessMap.value=m.clearcoatRoughnessMap,e(m.clearcoatRoughnessMap,p.clearcoatRoughnessMapTransform)),m.clearcoatNormalMap&&(p.clearcoatNormalMap.value=m.clearcoatNormalMap,e(m.clearcoatNormalMap,p.clearcoatNormalMapTransform),p.clearcoatNormalScale.value.copy(m.clearcoatNormalScale),m.side===We&&p.clearcoatNormalScale.value.negate())),m.dispersion>0&&(p.dispersion.value=m.dispersion),m.iridescence>0&&(p.iridescence.value=m.iridescence,p.iridescenceIOR.value=m.iridescenceIOR,p.iridescenceThicknessMinimum.value=m.iridescenceThicknessRange[0],p.iridescenceThicknessMaximum.value=m.iridescenceThicknessRange[1],m.iridescenceMap&&(p.iridescenceMap.value=m.iridescenceMap,e(m.iridescenceMap,p.iridescenceMapTransform)),m.iridescenceThicknessMap&&(p.iridescenceThicknessMap.value=m.iridescenceThicknessMap,e(m.iridescenceThicknessMap,p.iridescenceThicknessMapTransform))),m.transmission>0&&(p.transmission.value=m.transmission,p.transmissionSamplerMap.value=M.texture,p.transmissionSamplerSize.value.set(M.width,M.height),m.transmissionMap&&(p.transmissionMap.value=m.transmissionMap,e(m.transmissionMap,p.transmissionMapTransform)),p.thickness.value=m.thickness,m.thicknessMap&&(p.thicknessMap.value=m.thicknessMap,e(m.thicknessMap,p.thicknessMapTransform)),p.attenuationDistance.value=m.attenuationDistance,p.attenuationColor.value.copy(m.attenuationColor)),m.anisotropy>0&&(p.anisotropyVector.value.set(m.anisotropy*Math.cos(m.anisotropyRotation),m.anisotropy*Math.sin(m.anisotropyRotation)),m.anisotropyMap&&(p.anisotropyMap.value=m.anisotropyMap,e(m.anisotropyMap,p.anisotropyMapTransform))),p.specularIntensity.value=m.specularIntensity,p.specularColor.value.copy(m.specularColor),m.specularColorMap&&(p.specularColorMap.value=m.specularColorMap,e(m.specularColorMap,p.specularColorMapTransform)),m.specularIntensityMap&&(p.specularIntensityMap.value=m.specularIntensityMap,e(m.specularIntensityMap,p.specularIntensityMapTransform))}function _(p,m){m.matcap&&(p.matcap.value=m.matcap)}function g(p,m){const M=t.get(m).light;p.referencePosition.value.setFromMatrixPosition(M.matrixWorld),p.nearDistance.value=M.shadow.camera.near,p.farDistance.value=M.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:r}}function fM(i,t,e,n){let r={},s={},a=[];const o=i.getParameter(i.MAX_UNIFORM_BUFFER_BINDINGS);function l(M,T){const S=T.program;n.uniformBlockBinding(M,S)}function c(M,T){let S=r[M.id];S===void 0&&(_(M),S=u(M),r[M.id]=S,M.addEventListener("dispose",p));const b=T.program;n.updateUBOMapping(M,b);const A=t.render.frame;s[M.id]!==A&&(f(M),s[M.id]=A)}function u(M){const T=h();M.__bindingPointIndex=T;const S=i.createBuffer(),b=M.__size,A=M.usage;return i.bindBuffer(i.UNIFORM_BUFFER,S),i.bufferData(i.UNIFORM_BUFFER,b,A),i.bindBuffer(i.UNIFORM_BUFFER,null),i.bindBufferBase(i.UNIFORM_BUFFER,T,S),S}function h(){for(let M=0;M<o;M++)if(a.indexOf(M)===-1)return a.push(M),M;return Xt("WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function f(M){const T=r[M.id],S=M.uniforms,b=M.__cache;i.bindBuffer(i.UNIFORM_BUFFER,T);for(let A=0,R=S.length;A<R;A++){const x=Array.isArray(S[A])?S[A]:[S[A]];for(let y=0,G=x.length;y<G;y++){const D=x[y];if(d(D,A,y,b)===!0){const B=D.__offset,k=Array.isArray(D.value)?D.value:[D.value];let X=0;for(let C=0;C<k.length;C++){const L=k[C],P=g(L);typeof L=="number"||typeof L=="boolean"?(D.__data[0]=L,i.bufferSubData(i.UNIFORM_BUFFER,B+X,D.__data)):L.isMatrix3?(D.__data[0]=L.elements[0],D.__data[1]=L.elements[1],D.__data[2]=L.elements[2],D.__data[3]=0,D.__data[4]=L.elements[3],D.__data[5]=L.elements[4],D.__data[6]=L.elements[5],D.__data[7]=0,D.__data[8]=L.elements[6],D.__data[9]=L.elements[7],D.__data[10]=L.elements[8],D.__data[11]=0):(L.toArray(D.__data,X),X+=P.storage/Float32Array.BYTES_PER_ELEMENT)}i.bufferSubData(i.UNIFORM_BUFFER,B,D.__data)}}}i.bindBuffer(i.UNIFORM_BUFFER,null)}function d(M,T,S,b){const A=M.value,R=T+"_"+S;if(b[R]===void 0)return typeof A=="number"||typeof A=="boolean"?b[R]=A:b[R]=A.clone(),!0;{const x=b[R];if(typeof A=="number"||typeof A=="boolean"){if(x!==A)return b[R]=A,!0}else if(x.equals(A)===!1)return x.copy(A),!0}return!1}function _(M){const T=M.uniforms;let S=0;const b=16;for(let R=0,x=T.length;R<x;R++){const y=Array.isArray(T[R])?T[R]:[T[R]];for(let G=0,D=y.length;G<D;G++){const B=y[G],k=Array.isArray(B.value)?B.value:[B.value];for(let X=0,C=k.length;X<C;X++){const L=k[X],P=g(L),z=S%b,O=z%P.boundary,J=z+O;S+=O,J!==0&&b-J<P.storage&&(S+=b-J),B.__data=new Float32Array(P.storage/Float32Array.BYTES_PER_ELEMENT),B.__offset=S,S+=P.storage}}}const A=S%b;return A>0&&(S+=b-A),M.__size=S,M.__cache={},this}function g(M){const T={boundary:0,storage:0};return typeof M=="number"||typeof M=="boolean"?(T.boundary=4,T.storage=4):M.isVector2?(T.boundary=8,T.storage=8):M.isVector3||M.isColor?(T.boundary=16,T.storage=12):M.isVector4?(T.boundary=16,T.storage=16):M.isMatrix3?(T.boundary=48,T.storage=48):M.isMatrix4?(T.boundary=64,T.storage=64):M.isTexture?Pt("WebGLRenderer: Texture samplers can not be part of an uniforms group."):Pt("WebGLRenderer: Unsupported uniform value type.",M),T}function p(M){const T=M.target;T.removeEventListener("dispose",p);const S=a.indexOf(T.__bindingPointIndex);a.splice(S,1),i.deleteBuffer(r[T.id]),delete r[T.id],delete s[T.id]}function m(){for(const M in r)i.deleteBuffer(r[M]);a=[],r={},s={}}return{bind:l,update:c,dispose:m}}const hM=new Uint16Array([12469,15057,12620,14925,13266,14620,13807,14376,14323,13990,14545,13625,14713,13328,14840,12882,14931,12528,14996,12233,15039,11829,15066,11525,15080,11295,15085,10976,15082,10705,15073,10495,13880,14564,13898,14542,13977,14430,14158,14124,14393,13732,14556,13410,14702,12996,14814,12596,14891,12291,14937,11834,14957,11489,14958,11194,14943,10803,14921,10506,14893,10278,14858,9960,14484,14039,14487,14025,14499,13941,14524,13740,14574,13468,14654,13106,14743,12678,14818,12344,14867,11893,14889,11509,14893,11180,14881,10751,14852,10428,14812,10128,14765,9754,14712,9466,14764,13480,14764,13475,14766,13440,14766,13347,14769,13070,14786,12713,14816,12387,14844,11957,14860,11549,14868,11215,14855,10751,14825,10403,14782,10044,14729,9651,14666,9352,14599,9029,14967,12835,14966,12831,14963,12804,14954,12723,14936,12564,14917,12347,14900,11958,14886,11569,14878,11247,14859,10765,14828,10401,14784,10011,14727,9600,14660,9289,14586,8893,14508,8533,15111,12234,15110,12234,15104,12216,15092,12156,15067,12010,15028,11776,14981,11500,14942,11205,14902,10752,14861,10393,14812,9991,14752,9570,14682,9252,14603,8808,14519,8445,14431,8145,15209,11449,15208,11451,15202,11451,15190,11438,15163,11384,15117,11274,15055,10979,14994,10648,14932,10343,14871,9936,14803,9532,14729,9218,14645,8742,14556,8381,14461,8020,14365,7603,15273,10603,15272,10607,15267,10619,15256,10631,15231,10614,15182,10535,15118,10389,15042,10167,14963,9787,14883,9447,14800,9115,14710,8665,14615,8318,14514,7911,14411,7507,14279,7198,15314,9675,15313,9683,15309,9712,15298,9759,15277,9797,15229,9773,15166,9668,15084,9487,14995,9274,14898,8910,14800,8539,14697,8234,14590,7790,14479,7409,14367,7067,14178,6621,15337,8619,15337,8631,15333,8677,15325,8769,15305,8871,15264,8940,15202,8909,15119,8775,15022,8565,14916,8328,14804,8009,14688,7614,14569,7287,14448,6888,14321,6483,14088,6171,15350,7402,15350,7419,15347,7480,15340,7613,15322,7804,15287,7973,15229,8057,15148,8012,15046,7846,14933,7611,14810,7357,14682,7069,14552,6656,14421,6316,14251,5948,14007,5528,15356,5942,15356,5977,15353,6119,15348,6294,15332,6551,15302,6824,15249,7044,15171,7122,15070,7050,14949,6861,14818,6611,14679,6349,14538,6067,14398,5651,14189,5311,13935,4958,15359,4123,15359,4153,15356,4296,15353,4646,15338,5160,15311,5508,15263,5829,15188,6042,15088,6094,14966,6001,14826,5796,14678,5543,14527,5287,14377,4985,14133,4586,13869,4257,15360,1563,15360,1642,15358,2076,15354,2636,15341,3350,15317,4019,15273,4429,15203,4732,15105,4911,14981,4932,14836,4818,14679,4621,14517,4386,14359,4156,14083,3795,13808,3437,15360,122,15360,137,15358,285,15355,636,15344,1274,15322,2177,15281,2765,15215,3223,15120,3451,14995,3569,14846,3567,14681,3466,14511,3305,14344,3121,14037,2800,13753,2467,15360,0,15360,1,15359,21,15355,89,15346,253,15325,479,15287,796,15225,1148,15133,1492,15008,1749,14856,1882,14685,1886,14506,1783,14324,1608,13996,1398,13702,1183]);let yn=null;function dM(){return yn===null&&(yn=new o_(hM,16,16,Ir,ei),yn.name="DFG_LUT",yn.minFilter=Ie,yn.magFilter=Ie,yn.wrapS=Kn,yn.wrapT=Kn,yn.generateMipmaps=!1,yn.needsUpdate=!0),yn}class pM{constructor(t={}){const{canvas:e=Om(),context:n=null,depth:r=!0,stencil:s=!1,alpha:a=!1,antialias:o=!1,premultipliedAlpha:l=!0,preserveDrawingBuffer:c=!1,powerPreference:u="default",failIfMajorPerformanceCaveat:h=!1,reversedDepthBuffer:f=!1,outputBufferType:d=cn}=t;this.isWebGLRenderer=!0;let _;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");_=n.getContextAttributes().alpha}else _=a;const g=d,p=new Set([Tc,Ec,yc]),m=new Set([cn,Un,ps,ms,Mc,Sc]),M=new Uint32Array(4),T=new Int32Array(4);let S=null,b=null;const A=[],R=[];let x=null;this.domElement=e,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this.toneMapping=Cn,this.toneMappingExposure=1,this.transmissionResolutionScale=1;const y=this;let G=!1;this._outputColorSpace=on;let D=0,B=0,k=null,X=-1,C=null;const L=new me,P=new me;let z=null;const O=new Zt(0);let J=0,Q=e.width,st=e.height,bt=1,Ut=null,Ft=null;const K=new me(0,0,Q,st),nt=new me(0,0,Q,st);let lt=!1;const Lt=new Yh;let At=!1,Rt=!1;const ye=new ve,Gt=new W,Yt=new me,te={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let Ot=!1;function he(){return k===null?bt:1}let I=n;function _e(E,F){return e.getContext(E,F)}try{const E={alpha:!0,depth:r,stencil:s,antialias:o,premultipliedAlpha:l,preserveDrawingBuffer:c,powerPreference:u,failIfMajorPerformanceCaveat:h};if("setAttribute"in e&&e.setAttribute("data-engine",`three.js r${xc}`),e.addEventListener("webglcontextlost",gt,!1),e.addEventListener("webglcontextrestored",Ct,!1),e.addEventListener("webglcontextcreationerror",se,!1),I===null){const F="webgl2";if(I=_e(F,E),I===null)throw _e(F)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(E){throw Xt("WebGLRenderer: "+E.message),E}let qt,re,Mt,w,v,N,Z,j,$,mt,at,Tt,wt,tt,it,_t,xt,ht,Bt,U,ot,rt,pt;function et(){qt=new px(I),qt.init(),ot=new rM(I,qt),re=new ax(I,qt,t,ot),Mt=new nM(I,qt),re.reversedDepthBuffer&&f&&Mt.buffers.depth.setReversed(!0),w=new gx(I),v=new Gv,N=new iM(I,qt,Mt,v,re,ot,w),Z=new dx(y),j=new y_(I),rt=new rx(I,j),$=new mx(I,j,w,rt),mt=new vx(I,$,j,rt,w),ht=new xx(I,re,N),it=new ox(v),at=new Vv(y,Z,qt,re,rt,it),Tt=new uM(y,v),wt=new Wv,tt=new Zv(qt),xt=new ix(y,Z,Mt,mt,_,l),_t=new eM(y,mt,re),pt=new fM(I,w,re,Mt),Bt=new sx(I,qt,w),U=new _x(I,qt,w),w.programs=at.programs,y.capabilities=re,y.extensions=qt,y.properties=v,y.renderLists=wt,y.shadowMap=_t,y.state=Mt,y.info=w}et(),g!==cn&&(x=new Sx(g,e.width,e.height,r,s));const Y=new lM(y,I);this.xr=Y,this.getContext=function(){return I},this.getContextAttributes=function(){return I.getContextAttributes()},this.forceContextLoss=function(){const E=qt.get("WEBGL_lose_context");E&&E.loseContext()},this.forceContextRestore=function(){const E=qt.get("WEBGL_lose_context");E&&E.restoreContext()},this.getPixelRatio=function(){return bt},this.setPixelRatio=function(E){E!==void 0&&(bt=E,this.setSize(Q,st,!1))},this.getSize=function(E){return E.set(Q,st)},this.setSize=function(E,F,q=!0){if(Y.isPresenting){Pt("WebGLRenderer: Can't change size while VR device is presenting.");return}Q=E,st=F,e.width=Math.floor(E*bt),e.height=Math.floor(F*bt),q===!0&&(e.style.width=E+"px",e.style.height=F+"px"),x!==null&&x.setSize(e.width,e.height),this.setViewport(0,0,E,F)},this.getDrawingBufferSize=function(E){return E.set(Q*bt,st*bt).floor()},this.setDrawingBufferSize=function(E,F,q){Q=E,st=F,bt=q,e.width=Math.floor(E*q),e.height=Math.floor(F*q),this.setViewport(0,0,E,F)},this.setEffects=function(E){if(g===cn){console.error("THREE.WebGLRenderer: setEffects() requires outputBufferType set to HalfFloatType or FloatType.");return}if(E){for(let F=0;F<E.length;F++)if(E[F].isOutputPass===!0){console.warn("THREE.WebGLRenderer: OutputPass is not needed in setEffects(). Tone mapping and color space conversion are applied automatically.");break}}x.setEffects(E||[])},this.getCurrentViewport=function(E){return E.copy(L)},this.getViewport=function(E){return E.copy(K)},this.setViewport=function(E,F,q,H){E.isVector4?K.set(E.x,E.y,E.z,E.w):K.set(E,F,q,H),Mt.viewport(L.copy(K).multiplyScalar(bt).round())},this.getScissor=function(E){return E.copy(nt)},this.setScissor=function(E,F,q,H){E.isVector4?nt.set(E.x,E.y,E.z,E.w):nt.set(E,F,q,H),Mt.scissor(P.copy(nt).multiplyScalar(bt).round())},this.getScissorTest=function(){return lt},this.setScissorTest=function(E){Mt.setScissorTest(lt=E)},this.setOpaqueSort=function(E){Ut=E},this.setTransparentSort=function(E){Ft=E},this.getClearColor=function(E){return E.copy(xt.getClearColor())},this.setClearColor=function(){xt.setClearColor(...arguments)},this.getClearAlpha=function(){return xt.getClearAlpha()},this.setClearAlpha=function(){xt.setClearAlpha(...arguments)},this.clear=function(E=!0,F=!0,q=!0){let H=0;if(E){let V=!1;if(k!==null){const ut=k.texture.format;V=p.has(ut)}if(V){const ut=k.texture.type,dt=m.has(ut),ft=xt.getClearColor(),vt=xt.getClearAlpha(),yt=ft.r,Dt=ft.g,kt=ft.b;dt?(M[0]=yt,M[1]=Dt,M[2]=kt,M[3]=vt,I.clearBufferuiv(I.COLOR,0,M)):(T[0]=yt,T[1]=Dt,T[2]=kt,T[3]=vt,I.clearBufferiv(I.COLOR,0,T))}else H|=I.COLOR_BUFFER_BIT}F&&(H|=I.DEPTH_BUFFER_BIT),q&&(H|=I.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),H!==0&&I.clear(H)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){e.removeEventListener("webglcontextlost",gt,!1),e.removeEventListener("webglcontextrestored",Ct,!1),e.removeEventListener("webglcontextcreationerror",se,!1),xt.dispose(),wt.dispose(),tt.dispose(),v.dispose(),Z.dispose(),mt.dispose(),rt.dispose(),pt.dispose(),at.dispose(),Y.dispose(),Y.removeEventListener("sessionstart",Oc),Y.removeEventListener("sessionend",Bc),wi.stop()};function gt(E){E.preventDefault(),gu("WebGLRenderer: Context Lost."),G=!0}function Ct(){gu("WebGLRenderer: Context Restored."),G=!1;const E=w.autoReset,F=_t.enabled,q=_t.autoUpdate,H=_t.needsUpdate,V=_t.type;et(),w.autoReset=E,_t.enabled=F,_t.autoUpdate=q,_t.needsUpdate=H,_t.type=V}function se(E){Xt("WebGLRenderer: A WebGL context could not be created. Reason: ",E.statusMessage)}function $t(E){const F=E.target;F.removeEventListener("dispose",$t),Bn(F)}function Bn(E){kn(E),v.remove(E)}function kn(E){const F=v.get(E).programs;F!==void 0&&(F.forEach(function(q){at.releaseProgram(q)}),E.isShaderMaterial&&at.releaseShaderCache(E))}this.renderBufferDirect=function(E,F,q,H,V,ut){F===null&&(F=te);const dt=V.isMesh&&V.matrixWorld.determinant()<0,ft=Id(E,F,q,H,V);Mt.setMaterial(H,dt);let vt=q.index,yt=1;if(H.wireframe===!0){if(vt=$.getWireframeAttribute(q),vt===void 0)return;yt=2}const Dt=q.drawRange,kt=q.attributes.position;let Et=Dt.start*yt,Jt=(Dt.start+Dt.count)*yt;ut!==null&&(Et=Math.max(Et,ut.start*yt),Jt=Math.min(Jt,(ut.start+ut.count)*yt)),vt!==null?(Et=Math.max(Et,0),Jt=Math.min(Jt,vt.count)):kt!=null&&(Et=Math.max(Et,0),Jt=Math.min(Jt,kt.count));const de=Jt-Et;if(de<0||de===1/0)return;rt.setup(V,H,ft,q,vt);let ue,jt=Bt;if(vt!==null&&(ue=j.get(vt),jt=U,jt.setIndex(ue)),V.isMesh)H.wireframe===!0?(Mt.setLineWidth(H.wireframeLinewidth*he()),jt.setMode(I.LINES)):jt.setMode(I.TRIANGLES);else if(V.isLine){let Ce=H.linewidth;Ce===void 0&&(Ce=1),Mt.setLineWidth(Ce*he()),V.isLineSegments?jt.setMode(I.LINES):V.isLineLoop?jt.setMode(I.LINE_LOOP):jt.setMode(I.LINE_STRIP)}else V.isPoints?jt.setMode(I.POINTS):V.isSprite&&jt.setMode(I.TRIANGLES);if(V.isBatchedMesh)if(V._multiDrawInstances!==null)Aa("WebGLRenderer: renderMultiDrawInstances has been deprecated and will be removed in r184. Append to renderMultiDraw arguments and use indirection."),jt.renderMultiDrawInstances(V._multiDrawStarts,V._multiDrawCounts,V._multiDrawCount,V._multiDrawInstances);else if(qt.get("WEBGL_multi_draw"))jt.renderMultiDraw(V._multiDrawStarts,V._multiDrawCounts,V._multiDrawCount);else{const Ce=V._multiDrawStarts,St=V._multiDrawCounts,qe=V._multiDrawCount,Wt=vt?j.get(vt).bytesPerElement:1,hn=v.get(H).currentProgram.getUniforms();for(let Mn=0;Mn<qe;Mn++)hn.setValue(I,"_gl_DrawID",Mn),jt.render(Ce[Mn]/Wt,St[Mn])}else if(V.isInstancedMesh)jt.renderInstances(Et,de,V.count);else if(q.isInstancedBufferGeometry){const Ce=q._maxInstanceCount!==void 0?q._maxInstanceCount:1/0,St=Math.min(q.instanceCount,Ce);jt.renderInstances(Et,de,St)}else jt.render(Et,de)};function Fc(E,F,q){E.transparent===!0&&E.side===$n&&E.forceSinglePass===!1?(E.side=We,E.needsUpdate=!0,Cs(E,F,q),E.side=bi,E.needsUpdate=!0,Cs(E,F,q),E.side=$n):Cs(E,F,q)}this.compile=function(E,F,q=null){q===null&&(q=E),b=tt.get(q),b.init(F),R.push(b),q.traverseVisible(function(V){V.isLight&&V.layers.test(F.layers)&&(b.pushLight(V),V.castShadow&&b.pushShadow(V))}),E!==q&&E.traverseVisible(function(V){V.isLight&&V.layers.test(F.layers)&&(b.pushLight(V),V.castShadow&&b.pushShadow(V))}),b.setupLights();const H=new Set;return E.traverse(function(V){if(!(V.isMesh||V.isPoints||V.isLine||V.isSprite))return;const ut=V.material;if(ut)if(Array.isArray(ut))for(let dt=0;dt<ut.length;dt++){const ft=ut[dt];Fc(ft,q,V),H.add(ft)}else Fc(ut,q,V),H.add(ut)}),b=R.pop(),H},this.compileAsync=function(E,F,q=null){const H=this.compile(E,F,q);return new Promise(V=>{function ut(){if(H.forEach(function(dt){v.get(dt).currentProgram.isReady()&&H.delete(dt)}),H.size===0){V(E);return}setTimeout(ut,10)}qt.get("KHR_parallel_shader_compile")!==null?ut():setTimeout(ut,10)})};let Wa=null;function Ld(E){Wa&&Wa(E)}function Oc(){wi.stop()}function Bc(){wi.start()}const wi=new Qh;wi.setAnimationLoop(Ld),typeof self<"u"&&wi.setContext(self),this.setAnimationLoop=function(E){Wa=E,Y.setAnimationLoop(E),E===null?wi.stop():wi.start()},Y.addEventListener("sessionstart",Oc),Y.addEventListener("sessionend",Bc),this.render=function(E,F){if(F!==void 0&&F.isCamera!==!0){Xt("WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(G===!0)return;const q=Y.enabled===!0&&Y.isPresenting===!0,H=x!==null&&(k===null||q)&&x.begin(y,k);if(E.matrixWorldAutoUpdate===!0&&E.updateMatrixWorld(),F.parent===null&&F.matrixWorldAutoUpdate===!0&&F.updateMatrixWorld(),Y.enabled===!0&&Y.isPresenting===!0&&(x===null||x.isCompositing()===!1)&&(Y.cameraAutoUpdate===!0&&Y.updateCamera(F),F=Y.getCamera()),E.isScene===!0&&E.onBeforeRender(y,E,F,k),b=tt.get(E,R.length),b.init(F),R.push(b),ye.multiplyMatrices(F.projectionMatrix,F.matrixWorldInverse),Lt.setFromProjectionMatrix(ye,Rn,F.reversedDepth),Rt=this.localClippingEnabled,At=it.init(this.clippingPlanes,Rt),S=wt.get(E,A.length),S.init(),A.push(S),Y.enabled===!0&&Y.isPresenting===!0){const dt=y.xr.getDepthSensingMesh();dt!==null&&Xa(dt,F,-1/0,y.sortObjects)}Xa(E,F,0,y.sortObjects),S.finish(),y.sortObjects===!0&&S.sort(Ut,Ft),Ot=Y.enabled===!1||Y.isPresenting===!1||Y.hasDepthSensing()===!1,Ot&&xt.addToRenderList(S,E),this.info.render.frame++,At===!0&&it.beginShadows();const V=b.state.shadowsArray;if(_t.render(V,E,F),At===!0&&it.endShadows(),this.info.autoReset===!0&&this.info.reset(),(H&&x.hasRenderPass())===!1){const dt=S.opaque,ft=S.transmissive;if(b.setupLights(),F.isArrayCamera){const vt=F.cameras;if(ft.length>0)for(let yt=0,Dt=vt.length;yt<Dt;yt++){const kt=vt[yt];zc(dt,ft,E,kt)}Ot&&xt.render(E);for(let yt=0,Dt=vt.length;yt<Dt;yt++){const kt=vt[yt];kc(S,E,kt,kt.viewport)}}else ft.length>0&&zc(dt,ft,E,F),Ot&&xt.render(E),kc(S,E,F)}k!==null&&B===0&&(N.updateMultisampleRenderTarget(k),N.updateRenderTargetMipmap(k)),H&&x.end(y),E.isScene===!0&&E.onAfterRender(y,E,F),rt.resetDefaultState(),X=-1,C=null,R.pop(),R.length>0?(b=R[R.length-1],At===!0&&it.setGlobalState(y.clippingPlanes,b.state.camera)):b=null,A.pop(),A.length>0?S=A[A.length-1]:S=null};function Xa(E,F,q,H){if(E.visible===!1)return;if(E.layers.test(F.layers)){if(E.isGroup)q=E.renderOrder;else if(E.isLOD)E.autoUpdate===!0&&E.update(F);else if(E.isLight)b.pushLight(E),E.castShadow&&b.pushShadow(E);else if(E.isSprite){if(!E.frustumCulled||Lt.intersectsSprite(E)){H&&Yt.setFromMatrixPosition(E.matrixWorld).applyMatrix4(ye);const dt=mt.update(E),ft=E.material;ft.visible&&S.push(E,dt,ft,q,Yt.z,null)}}else if((E.isMesh||E.isLine||E.isPoints)&&(!E.frustumCulled||Lt.intersectsObject(E))){const dt=mt.update(E),ft=E.material;if(H&&(E.boundingSphere!==void 0?(E.boundingSphere===null&&E.computeBoundingSphere(),Yt.copy(E.boundingSphere.center)):(dt.boundingSphere===null&&dt.computeBoundingSphere(),Yt.copy(dt.boundingSphere.center)),Yt.applyMatrix4(E.matrixWorld).applyMatrix4(ye)),Array.isArray(ft)){const vt=dt.groups;for(let yt=0,Dt=vt.length;yt<Dt;yt++){const kt=vt[yt],Et=ft[kt.materialIndex];Et&&Et.visible&&S.push(E,dt,Et,q,Yt.z,kt)}}else ft.visible&&S.push(E,dt,ft,q,Yt.z,null)}}const ut=E.children;for(let dt=0,ft=ut.length;dt<ft;dt++)Xa(ut[dt],F,q,H)}function kc(E,F,q,H){const{opaque:V,transmissive:ut,transparent:dt}=E;b.setupLightsView(q),At===!0&&it.setGlobalState(y.clippingPlanes,q),H&&Mt.viewport(L.copy(H)),V.length>0&&Rs(V,F,q),ut.length>0&&Rs(ut,F,q),dt.length>0&&Rs(dt,F,q),Mt.buffers.depth.setTest(!0),Mt.buffers.depth.setMask(!0),Mt.buffers.color.setMask(!0),Mt.setPolygonOffset(!1)}function zc(E,F,q,H){if((q.isScene===!0?q.overrideMaterial:null)!==null)return;if(b.state.transmissionRenderTarget[H.id]===void 0){const Et=qt.has("EXT_color_buffer_half_float")||qt.has("EXT_color_buffer_float");b.state.transmissionRenderTarget[H.id]=new Pn(1,1,{generateMipmaps:!0,type:Et?ei:cn,minFilter:Hi,samples:Math.max(4,re.samples),stencilBuffer:s,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:Ht.workingColorSpace})}const ut=b.state.transmissionRenderTarget[H.id],dt=H.viewport||L;ut.setSize(dt.z*y.transmissionResolutionScale,dt.w*y.transmissionResolutionScale);const ft=y.getRenderTarget(),vt=y.getActiveCubeFace(),yt=y.getActiveMipmapLevel();y.setRenderTarget(ut),y.getClearColor(O),J=y.getClearAlpha(),J<1&&y.setClearColor(16777215,.5),y.clear(),Ot&&xt.render(q);const Dt=y.toneMapping;y.toneMapping=Cn;const kt=H.viewport;if(H.viewport!==void 0&&(H.viewport=void 0),b.setupLightsView(H),At===!0&&it.setGlobalState(y.clippingPlanes,H),Rs(E,q,H),N.updateMultisampleRenderTarget(ut),N.updateRenderTargetMipmap(ut),qt.has("WEBGL_multisampled_render_to_texture")===!1){let Et=!1;for(let Jt=0,de=F.length;Jt<de;Jt++){const ue=F[Jt],{object:jt,geometry:Ce,material:St,group:qe}=ue;if(St.side===$n&&jt.layers.test(H.layers)){const Wt=St.side;St.side=We,St.needsUpdate=!0,Vc(jt,q,H,Ce,St,qe),St.side=Wt,St.needsUpdate=!0,Et=!0}}Et===!0&&(N.updateMultisampleRenderTarget(ut),N.updateRenderTargetMipmap(ut))}y.setRenderTarget(ft,vt,yt),y.setClearColor(O,J),kt!==void 0&&(H.viewport=kt),y.toneMapping=Dt}function Rs(E,F,q){const H=F.isScene===!0?F.overrideMaterial:null;for(let V=0,ut=E.length;V<ut;V++){const dt=E[V],{object:ft,geometry:vt,group:yt}=dt;let Dt=dt.material;Dt.allowOverride===!0&&H!==null&&(Dt=H),ft.layers.test(q.layers)&&Vc(ft,F,q,vt,Dt,yt)}}function Vc(E,F,q,H,V,ut){E.onBeforeRender(y,F,q,H,V,ut),E.modelViewMatrix.multiplyMatrices(q.matrixWorldInverse,E.matrixWorld),E.normalMatrix.getNormalMatrix(E.modelViewMatrix),V.onBeforeRender(y,F,q,H,E,ut),V.transparent===!0&&V.side===$n&&V.forceSinglePass===!1?(V.side=We,V.needsUpdate=!0,y.renderBufferDirect(q,F,H,V,E,ut),V.side=bi,V.needsUpdate=!0,y.renderBufferDirect(q,F,H,V,E,ut),V.side=$n):y.renderBufferDirect(q,F,H,V,E,ut),E.onAfterRender(y,F,q,H,V,ut)}function Cs(E,F,q){F.isScene!==!0&&(F=te);const H=v.get(E),V=b.state.lights,ut=b.state.shadowsArray,dt=V.state.version,ft=at.getParameters(E,V.state,ut,F,q),vt=at.getProgramCacheKey(ft);let yt=H.programs;H.environment=E.isMeshStandardMaterial||E.isMeshLambertMaterial||E.isMeshPhongMaterial?F.environment:null,H.fog=F.fog;const Dt=E.isMeshStandardMaterial||E.isMeshLambertMaterial&&!E.envMap||E.isMeshPhongMaterial&&!E.envMap;H.envMap=Z.get(E.envMap||H.environment,Dt),H.envMapRotation=H.environment!==null&&E.envMap===null?F.environmentRotation:E.envMapRotation,yt===void 0&&(E.addEventListener("dispose",$t),yt=new Map,H.programs=yt);let kt=yt.get(vt);if(kt!==void 0){if(H.currentProgram===kt&&H.lightsStateVersion===dt)return Hc(E,ft),kt}else ft.uniforms=at.getUniforms(E),E.onBeforeCompile(ft,y),kt=at.acquireProgram(ft,vt),yt.set(vt,kt),H.uniforms=ft.uniforms;const Et=H.uniforms;return(!E.isShaderMaterial&&!E.isRawShaderMaterial||E.clipping===!0)&&(Et.clippingPlanes=it.uniform),Hc(E,ft),H.needsLights=Nd(E),H.lightsStateVersion=dt,H.needsLights&&(Et.ambientLightColor.value=V.state.ambient,Et.lightProbe.value=V.state.probe,Et.directionalLights.value=V.state.directional,Et.directionalLightShadows.value=V.state.directionalShadow,Et.spotLights.value=V.state.spot,Et.spotLightShadows.value=V.state.spotShadow,Et.rectAreaLights.value=V.state.rectArea,Et.ltc_1.value=V.state.rectAreaLTC1,Et.ltc_2.value=V.state.rectAreaLTC2,Et.pointLights.value=V.state.point,Et.pointLightShadows.value=V.state.pointShadow,Et.hemisphereLights.value=V.state.hemi,Et.directionalShadowMatrix.value=V.state.directionalShadowMatrix,Et.spotLightMatrix.value=V.state.spotLightMatrix,Et.spotLightMap.value=V.state.spotLightMap,Et.pointShadowMatrix.value=V.state.pointShadowMatrix),H.currentProgram=kt,H.uniformsList=null,kt}function Gc(E){if(E.uniformsList===null){const F=E.currentProgram.getUniforms();E.uniformsList=ha.seqWithValue(F.seq,E.uniforms)}return E.uniformsList}function Hc(E,F){const q=v.get(E);q.outputColorSpace=F.outputColorSpace,q.batching=F.batching,q.batchingColor=F.batchingColor,q.instancing=F.instancing,q.instancingColor=F.instancingColor,q.instancingMorph=F.instancingMorph,q.skinning=F.skinning,q.morphTargets=F.morphTargets,q.morphNormals=F.morphNormals,q.morphColors=F.morphColors,q.morphTargetsCount=F.morphTargetsCount,q.numClippingPlanes=F.numClippingPlanes,q.numIntersection=F.numClipIntersection,q.vertexAlphas=F.vertexAlphas,q.vertexTangents=F.vertexTangents,q.toneMapping=F.toneMapping}function Id(E,F,q,H,V){F.isScene!==!0&&(F=te),N.resetTextureUnits();const ut=F.fog,dt=H.isMeshStandardMaterial||H.isMeshLambertMaterial||H.isMeshPhongMaterial?F.environment:null,ft=k===null?y.outputColorSpace:k.isXRRenderTarget===!0?k.texture.colorSpace:Ur,vt=H.isMeshStandardMaterial||H.isMeshLambertMaterial&&!H.envMap||H.isMeshPhongMaterial&&!H.envMap,yt=Z.get(H.envMap||dt,vt),Dt=H.vertexColors===!0&&!!q.attributes.color&&q.attributes.color.itemSize===4,kt=!!q.attributes.tangent&&(!!H.normalMap||H.anisotropy>0),Et=!!q.morphAttributes.position,Jt=!!q.morphAttributes.normal,de=!!q.morphAttributes.color;let ue=Cn;H.toneMapped&&(k===null||k.isXRRenderTarget===!0)&&(ue=y.toneMapping);const jt=q.morphAttributes.position||q.morphAttributes.normal||q.morphAttributes.color,Ce=jt!==void 0?jt.length:0,St=v.get(H),qe=b.state.lights;if(At===!0&&(Rt===!0||E!==C)){const Ee=E===C&&H.id===X;it.setState(H,E,Ee)}let Wt=!1;H.version===St.__version?(St.needsLights&&St.lightsStateVersion!==qe.state.version||St.outputColorSpace!==ft||V.isBatchedMesh&&St.batching===!1||!V.isBatchedMesh&&St.batching===!0||V.isBatchedMesh&&St.batchingColor===!0&&V.colorTexture===null||V.isBatchedMesh&&St.batchingColor===!1&&V.colorTexture!==null||V.isInstancedMesh&&St.instancing===!1||!V.isInstancedMesh&&St.instancing===!0||V.isSkinnedMesh&&St.skinning===!1||!V.isSkinnedMesh&&St.skinning===!0||V.isInstancedMesh&&St.instancingColor===!0&&V.instanceColor===null||V.isInstancedMesh&&St.instancingColor===!1&&V.instanceColor!==null||V.isInstancedMesh&&St.instancingMorph===!0&&V.morphTexture===null||V.isInstancedMesh&&St.instancingMorph===!1&&V.morphTexture!==null||St.envMap!==yt||H.fog===!0&&St.fog!==ut||St.numClippingPlanes!==void 0&&(St.numClippingPlanes!==it.numPlanes||St.numIntersection!==it.numIntersection)||St.vertexAlphas!==Dt||St.vertexTangents!==kt||St.morphTargets!==Et||St.morphNormals!==Jt||St.morphColors!==de||St.toneMapping!==ue||St.morphTargetsCount!==Ce)&&(Wt=!0):(Wt=!0,St.__version=H.version);let hn=St.currentProgram;Wt===!0&&(hn=Cs(H,F,V));let Mn=!1,Ri=!1,tr=!1;const ee=hn.getUniforms(),Ae=St.uniforms;if(Mt.useProgram(hn.program)&&(Mn=!0,Ri=!0,tr=!0),H.id!==X&&(X=H.id,Ri=!0),Mn||C!==E){Mt.buffers.depth.getReversed()&&E.reversedDepth!==!0&&(E._reversedDepth=!0,E.updateProjectionMatrix()),ee.setValue(I,"projectionMatrix",E.projectionMatrix),ee.setValue(I,"viewMatrix",E.matrixWorldInverse);const oi=ee.map.cameraPosition;oi!==void 0&&oi.setValue(I,Gt.setFromMatrixPosition(E.matrixWorld)),re.logarithmicDepthBuffer&&ee.setValue(I,"logDepthBufFC",2/(Math.log(E.far+1)/Math.LN2)),(H.isMeshPhongMaterial||H.isMeshToonMaterial||H.isMeshLambertMaterial||H.isMeshBasicMaterial||H.isMeshStandardMaterial||H.isShaderMaterial)&&ee.setValue(I,"isOrthographic",E.isOrthographicCamera===!0),C!==E&&(C=E,Ri=!0,tr=!0)}if(St.needsLights&&(qe.state.directionalShadowMap.length>0&&ee.setValue(I,"directionalShadowMap",qe.state.directionalShadowMap,N),qe.state.spotShadowMap.length>0&&ee.setValue(I,"spotShadowMap",qe.state.spotShadowMap,N),qe.state.pointShadowMap.length>0&&ee.setValue(I,"pointShadowMap",qe.state.pointShadowMap,N)),V.isSkinnedMesh){ee.setOptional(I,V,"bindMatrix"),ee.setOptional(I,V,"bindMatrixInverse");const Ee=V.skeleton;Ee&&(Ee.boneTexture===null&&Ee.computeBoneTexture(),ee.setValue(I,"boneTexture",Ee.boneTexture,N))}V.isBatchedMesh&&(ee.setOptional(I,V,"batchingTexture"),ee.setValue(I,"batchingTexture",V._matricesTexture,N),ee.setOptional(I,V,"batchingIdTexture"),ee.setValue(I,"batchingIdTexture",V._indirectTexture,N),ee.setOptional(I,V,"batchingColorTexture"),V._colorsTexture!==null&&ee.setValue(I,"batchingColorTexture",V._colorsTexture,N));const ai=q.morphAttributes;if((ai.position!==void 0||ai.normal!==void 0||ai.color!==void 0)&&ht.update(V,q,hn),(Ri||St.receiveShadow!==V.receiveShadow)&&(St.receiveShadow=V.receiveShadow,ee.setValue(I,"receiveShadow",V.receiveShadow)),(H.isMeshStandardMaterial||H.isMeshLambertMaterial||H.isMeshPhongMaterial)&&H.envMap===null&&F.environment!==null&&(Ae.envMapIntensity.value=F.environmentIntensity),Ae.dfgLUT!==void 0&&(Ae.dfgLUT.value=dM()),Ri&&(ee.setValue(I,"toneMappingExposure",y.toneMappingExposure),St.needsLights&&Ud(Ae,tr),ut&&H.fog===!0&&Tt.refreshFogUniforms(Ae,ut),Tt.refreshMaterialUniforms(Ae,H,bt,st,b.state.transmissionRenderTarget[E.id]),ha.upload(I,Gc(St),Ae,N)),H.isShaderMaterial&&H.uniformsNeedUpdate===!0&&(ha.upload(I,Gc(St),Ae,N),H.uniformsNeedUpdate=!1),H.isSpriteMaterial&&ee.setValue(I,"center",V.center),ee.setValue(I,"modelViewMatrix",V.modelViewMatrix),ee.setValue(I,"normalMatrix",V.normalMatrix),ee.setValue(I,"modelMatrix",V.matrixWorld),H.isShaderMaterial||H.isRawShaderMaterial){const Ee=H.uniformsGroups;for(let oi=0,er=Ee.length;oi<er;oi++){const Wc=Ee[oi];pt.update(Wc,hn),pt.bind(Wc,hn)}}return hn}function Ud(E,F){E.ambientLightColor.needsUpdate=F,E.lightProbe.needsUpdate=F,E.directionalLights.needsUpdate=F,E.directionalLightShadows.needsUpdate=F,E.pointLights.needsUpdate=F,E.pointLightShadows.needsUpdate=F,E.spotLights.needsUpdate=F,E.spotLightShadows.needsUpdate=F,E.rectAreaLights.needsUpdate=F,E.hemisphereLights.needsUpdate=F}function Nd(E){return E.isMeshLambertMaterial||E.isMeshToonMaterial||E.isMeshPhongMaterial||E.isMeshStandardMaterial||E.isShadowMaterial||E.isShaderMaterial&&E.lights===!0}this.getActiveCubeFace=function(){return D},this.getActiveMipmapLevel=function(){return B},this.getRenderTarget=function(){return k},this.setRenderTargetTextures=function(E,F,q){const H=v.get(E);H.__autoAllocateDepthBuffer=E.resolveDepthBuffer===!1,H.__autoAllocateDepthBuffer===!1&&(H.__useRenderToTexture=!1),v.get(E.texture).__webglTexture=F,v.get(E.depthTexture).__webglTexture=H.__autoAllocateDepthBuffer?void 0:q,H.__hasExternalTextures=!0},this.setRenderTargetFramebuffer=function(E,F){const q=v.get(E);q.__webglFramebuffer=F,q.__useDefaultFramebuffer=F===void 0};const Fd=I.createFramebuffer();this.setRenderTarget=function(E,F=0,q=0){k=E,D=F,B=q;let H=null,V=!1,ut=!1;if(E){const ft=v.get(E);if(ft.__useDefaultFramebuffer!==void 0){Mt.bindFramebuffer(I.FRAMEBUFFER,ft.__webglFramebuffer),L.copy(E.viewport),P.copy(E.scissor),z=E.scissorTest,Mt.viewport(L),Mt.scissor(P),Mt.setScissorTest(z),X=-1;return}else if(ft.__webglFramebuffer===void 0)N.setupRenderTarget(E);else if(ft.__hasExternalTextures)N.rebindTextures(E,v.get(E.texture).__webglTexture,v.get(E.depthTexture).__webglTexture);else if(E.depthBuffer){const Dt=E.depthTexture;if(ft.__boundDepthTexture!==Dt){if(Dt!==null&&v.has(Dt)&&(E.width!==Dt.image.width||E.height!==Dt.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");N.setupDepthRenderbuffer(E)}}const vt=E.texture;(vt.isData3DTexture||vt.isDataArrayTexture||vt.isCompressedArrayTexture)&&(ut=!0);const yt=v.get(E).__webglFramebuffer;E.isWebGLCubeRenderTarget?(Array.isArray(yt[F])?H=yt[F][q]:H=yt[F],V=!0):E.samples>0&&N.useMultisampledRTT(E)===!1?H=v.get(E).__webglMultisampledFramebuffer:Array.isArray(yt)?H=yt[q]:H=yt,L.copy(E.viewport),P.copy(E.scissor),z=E.scissorTest}else L.copy(K).multiplyScalar(bt).floor(),P.copy(nt).multiplyScalar(bt).floor(),z=lt;if(q!==0&&(H=Fd),Mt.bindFramebuffer(I.FRAMEBUFFER,H)&&Mt.drawBuffers(E,H),Mt.viewport(L),Mt.scissor(P),Mt.setScissorTest(z),V){const ft=v.get(E.texture);I.framebufferTexture2D(I.FRAMEBUFFER,I.COLOR_ATTACHMENT0,I.TEXTURE_CUBE_MAP_POSITIVE_X+F,ft.__webglTexture,q)}else if(ut){const ft=F;for(let vt=0;vt<E.textures.length;vt++){const yt=v.get(E.textures[vt]);I.framebufferTextureLayer(I.FRAMEBUFFER,I.COLOR_ATTACHMENT0+vt,yt.__webglTexture,q,ft)}}else if(E!==null&&q!==0){const ft=v.get(E.texture);I.framebufferTexture2D(I.FRAMEBUFFER,I.COLOR_ATTACHMENT0,I.TEXTURE_2D,ft.__webglTexture,q)}X=-1},this.readRenderTargetPixels=function(E,F,q,H,V,ut,dt,ft=0){if(!(E&&E.isWebGLRenderTarget)){Xt("WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let vt=v.get(E).__webglFramebuffer;if(E.isWebGLCubeRenderTarget&&dt!==void 0&&(vt=vt[dt]),vt){Mt.bindFramebuffer(I.FRAMEBUFFER,vt);try{const yt=E.textures[ft],Dt=yt.format,kt=yt.type;if(E.textures.length>1&&I.readBuffer(I.COLOR_ATTACHMENT0+ft),!re.textureFormatReadable(Dt)){Xt("WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!re.textureTypeReadable(kt)){Xt("WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}F>=0&&F<=E.width-H&&q>=0&&q<=E.height-V&&I.readPixels(F,q,H,V,ot.convert(Dt),ot.convert(kt),ut)}finally{const yt=k!==null?v.get(k).__webglFramebuffer:null;Mt.bindFramebuffer(I.FRAMEBUFFER,yt)}}},this.readRenderTargetPixelsAsync=async function(E,F,q,H,V,ut,dt,ft=0){if(!(E&&E.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let vt=v.get(E).__webglFramebuffer;if(E.isWebGLCubeRenderTarget&&dt!==void 0&&(vt=vt[dt]),vt)if(F>=0&&F<=E.width-H&&q>=0&&q<=E.height-V){Mt.bindFramebuffer(I.FRAMEBUFFER,vt);const yt=E.textures[ft],Dt=yt.format,kt=yt.type;if(E.textures.length>1&&I.readBuffer(I.COLOR_ATTACHMENT0+ft),!re.textureFormatReadable(Dt))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!re.textureTypeReadable(kt))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");const Et=I.createBuffer();I.bindBuffer(I.PIXEL_PACK_BUFFER,Et),I.bufferData(I.PIXEL_PACK_BUFFER,ut.byteLength,I.STREAM_READ),I.readPixels(F,q,H,V,ot.convert(Dt),ot.convert(kt),0);const Jt=k!==null?v.get(k).__webglFramebuffer:null;Mt.bindFramebuffer(I.FRAMEBUFFER,Jt);const de=I.fenceSync(I.SYNC_GPU_COMMANDS_COMPLETE,0);return I.flush(),await Bm(I,de,4),I.bindBuffer(I.PIXEL_PACK_BUFFER,Et),I.getBufferSubData(I.PIXEL_PACK_BUFFER,0,ut),I.deleteBuffer(Et),I.deleteSync(de),ut}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")},this.copyFramebufferToTexture=function(E,F=null,q=0){const H=Math.pow(2,-q),V=Math.floor(E.image.width*H),ut=Math.floor(E.image.height*H),dt=F!==null?F.x:0,ft=F!==null?F.y:0;N.setTexture2D(E,0),I.copyTexSubImage2D(I.TEXTURE_2D,q,0,0,dt,ft,V,ut),Mt.unbindTexture()};const Od=I.createFramebuffer(),Bd=I.createFramebuffer();this.copyTextureToTexture=function(E,F,q=null,H=null,V=0,ut=0){let dt,ft,vt,yt,Dt,kt,Et,Jt,de;const ue=E.isCompressedTexture?E.mipmaps[ut]:E.image;if(q!==null)dt=q.max.x-q.min.x,ft=q.max.y-q.min.y,vt=q.isBox3?q.max.z-q.min.z:1,yt=q.min.x,Dt=q.min.y,kt=q.isBox3?q.min.z:0;else{const Ae=Math.pow(2,-V);dt=Math.floor(ue.width*Ae),ft=Math.floor(ue.height*Ae),E.isDataArrayTexture?vt=ue.depth:E.isData3DTexture?vt=Math.floor(ue.depth*Ae):vt=1,yt=0,Dt=0,kt=0}H!==null?(Et=H.x,Jt=H.y,de=H.z):(Et=0,Jt=0,de=0);const jt=ot.convert(F.format),Ce=ot.convert(F.type);let St;F.isData3DTexture?(N.setTexture3D(F,0),St=I.TEXTURE_3D):F.isDataArrayTexture||F.isCompressedArrayTexture?(N.setTexture2DArray(F,0),St=I.TEXTURE_2D_ARRAY):(N.setTexture2D(F,0),St=I.TEXTURE_2D),I.pixelStorei(I.UNPACK_FLIP_Y_WEBGL,F.flipY),I.pixelStorei(I.UNPACK_PREMULTIPLY_ALPHA_WEBGL,F.premultiplyAlpha),I.pixelStorei(I.UNPACK_ALIGNMENT,F.unpackAlignment);const qe=I.getParameter(I.UNPACK_ROW_LENGTH),Wt=I.getParameter(I.UNPACK_IMAGE_HEIGHT),hn=I.getParameter(I.UNPACK_SKIP_PIXELS),Mn=I.getParameter(I.UNPACK_SKIP_ROWS),Ri=I.getParameter(I.UNPACK_SKIP_IMAGES);I.pixelStorei(I.UNPACK_ROW_LENGTH,ue.width),I.pixelStorei(I.UNPACK_IMAGE_HEIGHT,ue.height),I.pixelStorei(I.UNPACK_SKIP_PIXELS,yt),I.pixelStorei(I.UNPACK_SKIP_ROWS,Dt),I.pixelStorei(I.UNPACK_SKIP_IMAGES,kt);const tr=E.isDataArrayTexture||E.isData3DTexture,ee=F.isDataArrayTexture||F.isData3DTexture;if(E.isDepthTexture){const Ae=v.get(E),ai=v.get(F),Ee=v.get(Ae.__renderTarget),oi=v.get(ai.__renderTarget);Mt.bindFramebuffer(I.READ_FRAMEBUFFER,Ee.__webglFramebuffer),Mt.bindFramebuffer(I.DRAW_FRAMEBUFFER,oi.__webglFramebuffer);for(let er=0;er<vt;er++)tr&&(I.framebufferTextureLayer(I.READ_FRAMEBUFFER,I.COLOR_ATTACHMENT0,v.get(E).__webglTexture,V,kt+er),I.framebufferTextureLayer(I.DRAW_FRAMEBUFFER,I.COLOR_ATTACHMENT0,v.get(F).__webglTexture,ut,de+er)),I.blitFramebuffer(yt,Dt,dt,ft,Et,Jt,dt,ft,I.DEPTH_BUFFER_BIT,I.NEAREST);Mt.bindFramebuffer(I.READ_FRAMEBUFFER,null),Mt.bindFramebuffer(I.DRAW_FRAMEBUFFER,null)}else if(V!==0||E.isRenderTargetTexture||v.has(E)){const Ae=v.get(E),ai=v.get(F);Mt.bindFramebuffer(I.READ_FRAMEBUFFER,Od),Mt.bindFramebuffer(I.DRAW_FRAMEBUFFER,Bd);for(let Ee=0;Ee<vt;Ee++)tr?I.framebufferTextureLayer(I.READ_FRAMEBUFFER,I.COLOR_ATTACHMENT0,Ae.__webglTexture,V,kt+Ee):I.framebufferTexture2D(I.READ_FRAMEBUFFER,I.COLOR_ATTACHMENT0,I.TEXTURE_2D,Ae.__webglTexture,V),ee?I.framebufferTextureLayer(I.DRAW_FRAMEBUFFER,I.COLOR_ATTACHMENT0,ai.__webglTexture,ut,de+Ee):I.framebufferTexture2D(I.DRAW_FRAMEBUFFER,I.COLOR_ATTACHMENT0,I.TEXTURE_2D,ai.__webglTexture,ut),V!==0?I.blitFramebuffer(yt,Dt,dt,ft,Et,Jt,dt,ft,I.COLOR_BUFFER_BIT,I.NEAREST):ee?I.copyTexSubImage3D(St,ut,Et,Jt,de+Ee,yt,Dt,dt,ft):I.copyTexSubImage2D(St,ut,Et,Jt,yt,Dt,dt,ft);Mt.bindFramebuffer(I.READ_FRAMEBUFFER,null),Mt.bindFramebuffer(I.DRAW_FRAMEBUFFER,null)}else ee?E.isDataTexture||E.isData3DTexture?I.texSubImage3D(St,ut,Et,Jt,de,dt,ft,vt,jt,Ce,ue.data):F.isCompressedArrayTexture?I.compressedTexSubImage3D(St,ut,Et,Jt,de,dt,ft,vt,jt,ue.data):I.texSubImage3D(St,ut,Et,Jt,de,dt,ft,vt,jt,Ce,ue):E.isDataTexture?I.texSubImage2D(I.TEXTURE_2D,ut,Et,Jt,dt,ft,jt,Ce,ue.data):E.isCompressedTexture?I.compressedTexSubImage2D(I.TEXTURE_2D,ut,Et,Jt,ue.width,ue.height,jt,ue.data):I.texSubImage2D(I.TEXTURE_2D,ut,Et,Jt,dt,ft,jt,Ce,ue);I.pixelStorei(I.UNPACK_ROW_LENGTH,qe),I.pixelStorei(I.UNPACK_IMAGE_HEIGHT,Wt),I.pixelStorei(I.UNPACK_SKIP_PIXELS,hn),I.pixelStorei(I.UNPACK_SKIP_ROWS,Mn),I.pixelStorei(I.UNPACK_SKIP_IMAGES,Ri),ut===0&&F.generateMipmaps&&I.generateMipmap(St),Mt.unbindTexture()},this.initRenderTarget=function(E){v.get(E).__webglFramebuffer===void 0&&N.setupRenderTarget(E)},this.initTexture=function(E){E.isCubeTexture?N.setTextureCube(E,0):E.isData3DTexture?N.setTexture3D(E,0):E.isDataArrayTexture||E.isCompressedArrayTexture?N.setTexture2DArray(E,0):N.setTexture2D(E,0),Mt.unbindTexture()},this.resetState=function(){D=0,B=0,k=null,Mt.reset(),rt.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Rn}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(t){this._outputColorSpace=t;const e=this.getContext();e.drawingBufferColorSpace=Ht._getDrawingBufferColorSpace(t),e.unpackColorSpace=Ht._getUnpackColorSpace()}}var mM={value:()=>{}};function sd(){for(var i=0,t=arguments.length,e={},n;i<t;++i){if(!(n=arguments[i]+"")||n in e||/[\s.]/.test(n))throw new Error("illegal type: "+n);e[n]=[]}return new da(e)}function da(i){this._=i}function _M(i,t){return i.trim().split(/^|\s+/).map(function(e){var n="",r=e.indexOf(".");if(r>=0&&(n=e.slice(r+1),e=e.slice(0,r)),e&&!t.hasOwnProperty(e))throw new Error("unknown type: "+e);return{type:e,name:n}})}da.prototype=sd.prototype={constructor:da,on:function(i,t){var e=this._,n=_M(i+"",e),r,s=-1,a=n.length;if(arguments.length<2){for(;++s<a;)if((r=(i=n[s]).type)&&(r=gM(e[r],i.name)))return r;return}if(t!=null&&typeof t!="function")throw new Error("invalid callback: "+t);for(;++s<a;)if(r=(i=n[s]).type)e[r]=sf(e[r],i.name,t);else if(t==null)for(r in e)e[r]=sf(e[r],i.name,null);return this},copy:function(){var i={},t=this._;for(var e in t)i[e]=t[e].slice();return new da(i)},call:function(i,t){if((r=arguments.length-2)>0)for(var e=new Array(r),n=0,r,s;n<r;++n)e[n]=arguments[n+2];if(!this._.hasOwnProperty(i))throw new Error("unknown type: "+i);for(s=this._[i],n=0,r=s.length;n<r;++n)s[n].value.apply(t,e)},apply:function(i,t,e){if(!this._.hasOwnProperty(i))throw new Error("unknown type: "+i);for(var n=this._[i],r=0,s=n.length;r<s;++r)n[r].value.apply(t,e)}};function gM(i,t){for(var e=0,n=i.length,r;e<n;++e)if((r=i[e]).name===t)return r.value}function sf(i,t,e){for(var n=0,r=i.length;n<r;++n)if(i[n].name===t){i[n]=mM,i=i.slice(0,n).concat(i.slice(n+1));break}return e!=null&&i.push({name:t,value:e}),i}var Wl="http://www.w3.org/1999/xhtml";const af={svg:"http://www.w3.org/2000/svg",xhtml:Wl,xlink:"http://www.w3.org/1999/xlink",xml:"http://www.w3.org/XML/1998/namespace",xmlns:"http://www.w3.org/2000/xmlns/"};function Va(i){var t=i+="",e=t.indexOf(":");return e>=0&&(t=i.slice(0,e))!=="xmlns"&&(i=i.slice(e+1)),af.hasOwnProperty(t)?{space:af[t],local:i}:i}function xM(i){return function(){var t=this.ownerDocument,e=this.namespaceURI;return e===Wl&&t.documentElement.namespaceURI===Wl?t.createElement(i):t.createElementNS(e,i)}}function vM(i){return function(){return this.ownerDocument.createElementNS(i.space,i.local)}}function ad(i){var t=Va(i);return(t.local?vM:xM)(t)}function MM(){}function Pc(i){return i==null?MM:function(){return this.querySelector(i)}}function SM(i){typeof i!="function"&&(i=Pc(i));for(var t=this._groups,e=t.length,n=new Array(e),r=0;r<e;++r)for(var s=t[r],a=s.length,o=n[r]=new Array(a),l,c,u=0;u<a;++u)(l=s[u])&&(c=i.call(l,l.__data__,u,s))&&("__data__"in l&&(c.__data__=l.__data__),o[u]=c);return new rn(n,this._parents)}function yM(i){return i==null?[]:Array.isArray(i)?i:Array.from(i)}function EM(){return[]}function od(i){return i==null?EM:function(){return this.querySelectorAll(i)}}function TM(i){return function(){return yM(i.apply(this,arguments))}}function bM(i){typeof i=="function"?i=TM(i):i=od(i);for(var t=this._groups,e=t.length,n=[],r=[],s=0;s<e;++s)for(var a=t[s],o=a.length,l,c=0;c<o;++c)(l=a[c])&&(n.push(i.call(l,l.__data__,c,a)),r.push(l));return new rn(n,r)}function ld(i){return function(){return this.matches(i)}}function cd(i){return function(t){return t.matches(i)}}var AM=Array.prototype.find;function wM(i){return function(){return AM.call(this.children,i)}}function RM(){return this.firstElementChild}function CM(i){return this.select(i==null?RM:wM(typeof i=="function"?i:cd(i)))}var PM=Array.prototype.filter;function DM(){return Array.from(this.children)}function LM(i){return function(){return PM.call(this.children,i)}}function IM(i){return this.selectAll(i==null?DM:LM(typeof i=="function"?i:cd(i)))}function UM(i){typeof i!="function"&&(i=ld(i));for(var t=this._groups,e=t.length,n=new Array(e),r=0;r<e;++r)for(var s=t[r],a=s.length,o=n[r]=[],l,c=0;c<a;++c)(l=s[c])&&i.call(l,l.__data__,c,s)&&o.push(l);return new rn(n,this._parents)}function ud(i){return new Array(i.length)}function NM(){return new rn(this._enter||this._groups.map(ud),this._parents)}function wa(i,t){this.ownerDocument=i.ownerDocument,this.namespaceURI=i.namespaceURI,this._next=null,this._parent=i,this.__data__=t}wa.prototype={constructor:wa,appendChild:function(i){return this._parent.insertBefore(i,this._next)},insertBefore:function(i,t){return this._parent.insertBefore(i,t)},querySelector:function(i){return this._parent.querySelector(i)},querySelectorAll:function(i){return this._parent.querySelectorAll(i)}};function FM(i){return function(){return i}}function OM(i,t,e,n,r,s){for(var a=0,o,l=t.length,c=s.length;a<c;++a)(o=t[a])?(o.__data__=s[a],n[a]=o):e[a]=new wa(i,s[a]);for(;a<l;++a)(o=t[a])&&(r[a]=o)}function BM(i,t,e,n,r,s,a){var o,l,c=new Map,u=t.length,h=s.length,f=new Array(u),d;for(o=0;o<u;++o)(l=t[o])&&(f[o]=d=a.call(l,l.__data__,o,t)+"",c.has(d)?r[o]=l:c.set(d,l));for(o=0;o<h;++o)d=a.call(i,s[o],o,s)+"",(l=c.get(d))?(n[o]=l,l.__data__=s[o],c.delete(d)):e[o]=new wa(i,s[o]);for(o=0;o<u;++o)(l=t[o])&&c.get(f[o])===l&&(r[o]=l)}function kM(i){return i.__data__}function zM(i,t){if(!arguments.length)return Array.from(this,kM);var e=t?BM:OM,n=this._parents,r=this._groups;typeof i!="function"&&(i=FM(i));for(var s=r.length,a=new Array(s),o=new Array(s),l=new Array(s),c=0;c<s;++c){var u=n[c],h=r[c],f=h.length,d=VM(i.call(u,u&&u.__data__,c,n)),_=d.length,g=o[c]=new Array(_),p=a[c]=new Array(_),m=l[c]=new Array(f);e(u,h,g,p,m,d,t);for(var M=0,T=0,S,b;M<_;++M)if(S=g[M]){for(M>=T&&(T=M+1);!(b=p[T])&&++T<_;);S._next=b||null}}return a=new rn(a,n),a._enter=o,a._exit=l,a}function VM(i){return typeof i=="object"&&"length"in i?i:Array.from(i)}function GM(){return new rn(this._exit||this._groups.map(ud),this._parents)}function HM(i,t,e){var n=this.enter(),r=this,s=this.exit();return typeof i=="function"?(n=i(n),n&&(n=n.selection())):n=n.append(i+""),t!=null&&(r=t(r),r&&(r=r.selection())),e==null?s.remove():e(s),n&&r?n.merge(r).order():r}function WM(i){for(var t=i.selection?i.selection():i,e=this._groups,n=t._groups,r=e.length,s=n.length,a=Math.min(r,s),o=new Array(r),l=0;l<a;++l)for(var c=e[l],u=n[l],h=c.length,f=o[l]=new Array(h),d,_=0;_<h;++_)(d=c[_]||u[_])&&(f[_]=d);for(;l<r;++l)o[l]=e[l];return new rn(o,this._parents)}function XM(){for(var i=this._groups,t=-1,e=i.length;++t<e;)for(var n=i[t],r=n.length-1,s=n[r],a;--r>=0;)(a=n[r])&&(s&&a.compareDocumentPosition(s)^4&&s.parentNode.insertBefore(a,s),s=a);return this}function qM(i){i||(i=YM);function t(h,f){return h&&f?i(h.__data__,f.__data__):!h-!f}for(var e=this._groups,n=e.length,r=new Array(n),s=0;s<n;++s){for(var a=e[s],o=a.length,l=r[s]=new Array(o),c,u=0;u<o;++u)(c=a[u])&&(l[u]=c);l.sort(t)}return new rn(r,this._parents).order()}function YM(i,t){return i<t?-1:i>t?1:i>=t?0:NaN}function $M(){var i=arguments[0];return arguments[0]=this,i.apply(null,arguments),this}function KM(){return Array.from(this)}function ZM(){for(var i=this._groups,t=0,e=i.length;t<e;++t)for(var n=i[t],r=0,s=n.length;r<s;++r){var a=n[r];if(a)return a}return null}function JM(){let i=0;for(const t of this)++i;return i}function jM(){return!this.node()}function QM(i){for(var t=this._groups,e=0,n=t.length;e<n;++e)for(var r=t[e],s=0,a=r.length,o;s<a;++s)(o=r[s])&&i.call(o,o.__data__,s,r);return this}function tS(i){return function(){this.removeAttribute(i)}}function eS(i){return function(){this.removeAttributeNS(i.space,i.local)}}function nS(i,t){return function(){this.setAttribute(i,t)}}function iS(i,t){return function(){this.setAttributeNS(i.space,i.local,t)}}function rS(i,t){return function(){var e=t.apply(this,arguments);e==null?this.removeAttribute(i):this.setAttribute(i,e)}}function sS(i,t){return function(){var e=t.apply(this,arguments);e==null?this.removeAttributeNS(i.space,i.local):this.setAttributeNS(i.space,i.local,e)}}function aS(i,t){var e=Va(i);if(arguments.length<2){var n=this.node();return e.local?n.getAttributeNS(e.space,e.local):n.getAttribute(e)}return this.each((t==null?e.local?eS:tS:typeof t=="function"?e.local?sS:rS:e.local?iS:nS)(e,t))}function fd(i){return i.ownerDocument&&i.ownerDocument.defaultView||i.document&&i||i.defaultView}function oS(i){return function(){this.style.removeProperty(i)}}function lS(i,t,e){return function(){this.style.setProperty(i,t,e)}}function cS(i,t,e){return function(){var n=t.apply(this,arguments);n==null?this.style.removeProperty(i):this.style.setProperty(i,n,e)}}function uS(i,t,e){return arguments.length>1?this.each((t==null?oS:typeof t=="function"?cS:lS)(i,t,e??"")):Fr(this.node(),i)}function Fr(i,t){return i.style.getPropertyValue(t)||fd(i).getComputedStyle(i,null).getPropertyValue(t)}function fS(i){return function(){delete this[i]}}function hS(i,t){return function(){this[i]=t}}function dS(i,t){return function(){var e=t.apply(this,arguments);e==null?delete this[i]:this[i]=e}}function pS(i,t){return arguments.length>1?this.each((t==null?fS:typeof t=="function"?dS:hS)(i,t)):this.node()[i]}function hd(i){return i.trim().split(/^|\s+/)}function Dc(i){return i.classList||new dd(i)}function dd(i){this._node=i,this._names=hd(i.getAttribute("class")||"")}dd.prototype={add:function(i){var t=this._names.indexOf(i);t<0&&(this._names.push(i),this._node.setAttribute("class",this._names.join(" ")))},remove:function(i){var t=this._names.indexOf(i);t>=0&&(this._names.splice(t,1),this._node.setAttribute("class",this._names.join(" ")))},contains:function(i){return this._names.indexOf(i)>=0}};function pd(i,t){for(var e=Dc(i),n=-1,r=t.length;++n<r;)e.add(t[n])}function md(i,t){for(var e=Dc(i),n=-1,r=t.length;++n<r;)e.remove(t[n])}function mS(i){return function(){pd(this,i)}}function _S(i){return function(){md(this,i)}}function gS(i,t){return function(){(t.apply(this,arguments)?pd:md)(this,i)}}function xS(i,t){var e=hd(i+"");if(arguments.length<2){for(var n=Dc(this.node()),r=-1,s=e.length;++r<s;)if(!n.contains(e[r]))return!1;return!0}return this.each((typeof t=="function"?gS:t?mS:_S)(e,t))}function vS(){this.textContent=""}function MS(i){return function(){this.textContent=i}}function SS(i){return function(){var t=i.apply(this,arguments);this.textContent=t??""}}function yS(i){return arguments.length?this.each(i==null?vS:(typeof i=="function"?SS:MS)(i)):this.node().textContent}function ES(){this.innerHTML=""}function TS(i){return function(){this.innerHTML=i}}function bS(i){return function(){var t=i.apply(this,arguments);this.innerHTML=t??""}}function AS(i){return arguments.length?this.each(i==null?ES:(typeof i=="function"?bS:TS)(i)):this.node().innerHTML}function wS(){this.nextSibling&&this.parentNode.appendChild(this)}function RS(){return this.each(wS)}function CS(){this.previousSibling&&this.parentNode.insertBefore(this,this.parentNode.firstChild)}function PS(){return this.each(CS)}function DS(i){var t=typeof i=="function"?i:ad(i);return this.select(function(){return this.appendChild(t.apply(this,arguments))})}function LS(){return null}function IS(i,t){var e=typeof i=="function"?i:ad(i),n=t==null?LS:typeof t=="function"?t:Pc(t);return this.select(function(){return this.insertBefore(e.apply(this,arguments),n.apply(this,arguments)||null)})}function US(){var i=this.parentNode;i&&i.removeChild(this)}function NS(){return this.each(US)}function FS(){var i=this.cloneNode(!1),t=this.parentNode;return t?t.insertBefore(i,this.nextSibling):i}function OS(){var i=this.cloneNode(!0),t=this.parentNode;return t?t.insertBefore(i,this.nextSibling):i}function BS(i){return this.select(i?OS:FS)}function kS(i){return arguments.length?this.property("__data__",i):this.node().__data__}function zS(i){return function(t){i.call(this,t,this.__data__)}}function VS(i){return i.trim().split(/^|\s+/).map(function(t){var e="",n=t.indexOf(".");return n>=0&&(e=t.slice(n+1),t=t.slice(0,n)),{type:t,name:e}})}function GS(i){return function(){var t=this.__on;if(t){for(var e=0,n=-1,r=t.length,s;e<r;++e)s=t[e],(!i.type||s.type===i.type)&&s.name===i.name?this.removeEventListener(s.type,s.listener,s.options):t[++n]=s;++n?t.length=n:delete this.__on}}}function HS(i,t,e){return function(){var n=this.__on,r,s=zS(t);if(n){for(var a=0,o=n.length;a<o;++a)if((r=n[a]).type===i.type&&r.name===i.name){this.removeEventListener(r.type,r.listener,r.options),this.addEventListener(r.type,r.listener=s,r.options=e),r.value=t;return}}this.addEventListener(i.type,s,e),r={type:i.type,name:i.name,value:t,listener:s,options:e},n?n.push(r):this.__on=[r]}}function WS(i,t,e){var n=VS(i+""),r,s=n.length,a;if(arguments.length<2){var o=this.node().__on;if(o){for(var l=0,c=o.length,u;l<c;++l)for(r=0,u=o[l];r<s;++r)if((a=n[r]).type===u.type&&a.name===u.name)return u.value}return}for(o=t?HS:GS,r=0;r<s;++r)this.each(o(n[r],t,e));return this}function _d(i,t,e){var n=fd(i),r=n.CustomEvent;typeof r=="function"?r=new r(t,e):(r=n.document.createEvent("Event"),e?(r.initEvent(t,e.bubbles,e.cancelable),r.detail=e.detail):r.initEvent(t,!1,!1)),i.dispatchEvent(r)}function XS(i,t){return function(){return _d(this,i,t)}}function qS(i,t){return function(){return _d(this,i,t.apply(this,arguments))}}function YS(i,t){return this.each((typeof t=="function"?qS:XS)(i,t))}function*$S(){for(var i=this._groups,t=0,e=i.length;t<e;++t)for(var n=i[t],r=0,s=n.length,a;r<s;++r)(a=n[r])&&(yield a)}var gd=[null];function rn(i,t){this._groups=i,this._parents=t}function As(){return new rn([[document.documentElement]],gd)}function KS(){return this}rn.prototype=As.prototype={constructor:rn,select:SM,selectAll:bM,selectChild:CM,selectChildren:IM,filter:UM,data:zM,enter:NM,exit:GM,join:HM,merge:WM,selection:KS,order:XM,sort:qM,call:$M,nodes:KM,node:ZM,size:JM,empty:jM,each:QM,attr:aS,style:uS,property:pS,classed:xS,text:yS,html:AS,raise:RS,lower:PS,append:DS,insert:IS,remove:NS,clone:BS,datum:kS,on:WS,dispatch:YS,[Symbol.iterator]:$S};function ZS(i){return typeof i=="string"?new rn([[document.querySelector(i)]],[document.documentElement]):new rn([[i]],gd)}function Lc(i,t,e){i.prototype=t.prototype=e,e.constructor=i}function xd(i,t){var e=Object.create(i.prototype);for(var n in t)e[n]=t[n];return e}function ws(){}var gs=.7,Ra=1/gs,Tr="\\s*([+-]?\\d+)\\s*",xs="\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)\\s*",Ln="\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)%\\s*",JS=/^#([0-9a-f]{3,8})$/,jS=new RegExp(`^rgb\\(${Tr},${Tr},${Tr}\\)$`),QS=new RegExp(`^rgb\\(${Ln},${Ln},${Ln}\\)$`),ty=new RegExp(`^rgba\\(${Tr},${Tr},${Tr},${xs}\\)$`),ey=new RegExp(`^rgba\\(${Ln},${Ln},${Ln},${xs}\\)$`),ny=new RegExp(`^hsl\\(${xs},${Ln},${Ln}\\)$`),iy=new RegExp(`^hsla\\(${xs},${Ln},${Ln},${xs}\\)$`),of={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074};Lc(ws,vs,{copy(i){return Object.assign(new this.constructor,this,i)},displayable(){return this.rgb().displayable()},hex:lf,formatHex:lf,formatHex8:ry,formatHsl:sy,formatRgb:cf,toString:cf});function lf(){return this.rgb().formatHex()}function ry(){return this.rgb().formatHex8()}function sy(){return vd(this).formatHsl()}function cf(){return this.rgb().formatRgb()}function vs(i){var t,e;return i=(i+"").trim().toLowerCase(),(t=JS.exec(i))?(e=t[1].length,t=parseInt(t[1],16),e===6?uf(t):e===3?new ke(t>>8&15|t>>4&240,t>>4&15|t&240,(t&15)<<4|t&15,1):e===8?ta(t>>24&255,t>>16&255,t>>8&255,(t&255)/255):e===4?ta(t>>12&15|t>>8&240,t>>8&15|t>>4&240,t>>4&15|t&240,((t&15)<<4|t&15)/255):null):(t=jS.exec(i))?new ke(t[1],t[2],t[3],1):(t=QS.exec(i))?new ke(t[1]*255/100,t[2]*255/100,t[3]*255/100,1):(t=ty.exec(i))?ta(t[1],t[2],t[3],t[4]):(t=ey.exec(i))?ta(t[1]*255/100,t[2]*255/100,t[3]*255/100,t[4]):(t=ny.exec(i))?df(t[1],t[2]/100,t[3]/100,1):(t=iy.exec(i))?df(t[1],t[2]/100,t[3]/100,t[4]):of.hasOwnProperty(i)?uf(of[i]):i==="transparent"?new ke(NaN,NaN,NaN,0):null}function uf(i){return new ke(i>>16&255,i>>8&255,i&255,1)}function ta(i,t,e,n){return n<=0&&(i=t=e=NaN),new ke(i,t,e,n)}function ay(i){return i instanceof ws||(i=vs(i)),i?(i=i.rgb(),new ke(i.r,i.g,i.b,i.opacity)):new ke}function Xl(i,t,e,n){return arguments.length===1?ay(i):new ke(i,t,e,n??1)}function ke(i,t,e,n){this.r=+i,this.g=+t,this.b=+e,this.opacity=+n}Lc(ke,Xl,xd(ws,{brighter(i){return i=i==null?Ra:Math.pow(Ra,i),new ke(this.r*i,this.g*i,this.b*i,this.opacity)},darker(i){return i=i==null?gs:Math.pow(gs,i),new ke(this.r*i,this.g*i,this.b*i,this.opacity)},rgb(){return this},clamp(){return new ke(Zi(this.r),Zi(this.g),Zi(this.b),Ca(this.opacity))},displayable(){return-.5<=this.r&&this.r<255.5&&-.5<=this.g&&this.g<255.5&&-.5<=this.b&&this.b<255.5&&0<=this.opacity&&this.opacity<=1},hex:ff,formatHex:ff,formatHex8:oy,formatRgb:hf,toString:hf}));function ff(){return`#${Xi(this.r)}${Xi(this.g)}${Xi(this.b)}`}function oy(){return`#${Xi(this.r)}${Xi(this.g)}${Xi(this.b)}${Xi((isNaN(this.opacity)?1:this.opacity)*255)}`}function hf(){const i=Ca(this.opacity);return`${i===1?"rgb(":"rgba("}${Zi(this.r)}, ${Zi(this.g)}, ${Zi(this.b)}${i===1?")":`, ${i})`}`}function Ca(i){return isNaN(i)?1:Math.max(0,Math.min(1,i))}function Zi(i){return Math.max(0,Math.min(255,Math.round(i)||0))}function Xi(i){return i=Zi(i),(i<16?"0":"")+i.toString(16)}function df(i,t,e,n){return n<=0?i=t=e=NaN:e<=0||e>=1?i=t=NaN:t<=0&&(i=NaN),new gn(i,t,e,n)}function vd(i){if(i instanceof gn)return new gn(i.h,i.s,i.l,i.opacity);if(i instanceof ws||(i=vs(i)),!i)return new gn;if(i instanceof gn)return i;i=i.rgb();var t=i.r/255,e=i.g/255,n=i.b/255,r=Math.min(t,e,n),s=Math.max(t,e,n),a=NaN,o=s-r,l=(s+r)/2;return o?(t===s?a=(e-n)/o+(e<n)*6:e===s?a=(n-t)/o+2:a=(t-e)/o+4,o/=l<.5?s+r:2-s-r,a*=60):o=l>0&&l<1?0:a,new gn(a,o,l,i.opacity)}function ly(i,t,e,n){return arguments.length===1?vd(i):new gn(i,t,e,n??1)}function gn(i,t,e,n){this.h=+i,this.s=+t,this.l=+e,this.opacity=+n}Lc(gn,ly,xd(ws,{brighter(i){return i=i==null?Ra:Math.pow(Ra,i),new gn(this.h,this.s,this.l*i,this.opacity)},darker(i){return i=i==null?gs:Math.pow(gs,i),new gn(this.h,this.s,this.l*i,this.opacity)},rgb(){var i=this.h%360+(this.h<0)*360,t=isNaN(i)||isNaN(this.s)?0:this.s,e=this.l,n=e+(e<.5?e:1-e)*t,r=2*e-n;return new ke(Uo(i>=240?i-240:i+120,r,n),Uo(i,r,n),Uo(i<120?i+240:i-120,r,n),this.opacity)},clamp(){return new gn(pf(this.h),ea(this.s),ea(this.l),Ca(this.opacity))},displayable(){return(0<=this.s&&this.s<=1||isNaN(this.s))&&0<=this.l&&this.l<=1&&0<=this.opacity&&this.opacity<=1},formatHsl(){const i=Ca(this.opacity);return`${i===1?"hsl(":"hsla("}${pf(this.h)}, ${ea(this.s)*100}%, ${ea(this.l)*100}%${i===1?")":`, ${i})`}`}}));function pf(i){return i=(i||0)%360,i<0?i+360:i}function ea(i){return Math.max(0,Math.min(1,i||0))}function Uo(i,t,e){return(i<60?t+(e-t)*i/60:i<180?e:i<240?t+(e-t)*(240-i)/60:t)*255}const Md=i=>()=>i;function cy(i,t){return function(e){return i+e*t}}function uy(i,t,e){return i=Math.pow(i,e),t=Math.pow(t,e)-i,e=1/e,function(n){return Math.pow(i+n*t,e)}}function fy(i){return(i=+i)==1?Sd:function(t,e){return e-t?uy(t,e,i):Md(isNaN(t)?e:t)}}function Sd(i,t){var e=t-i;return e?cy(i,e):Md(isNaN(i)?t:i)}const mf=function i(t){var e=fy(t);function n(r,s){var a=e((r=Xl(r)).r,(s=Xl(s)).r),o=e(r.g,s.g),l=e(r.b,s.b),c=Sd(r.opacity,s.opacity);return function(u){return r.r=a(u),r.g=o(u),r.b=l(u),r.opacity=c(u),r+""}}return n.gamma=i,n}(1);function pi(i,t){return i=+i,t=+t,function(e){return i*(1-e)+t*e}}var ql=/[-+]?(?:\d+\.?\d*|\.?\d+)(?:[eE][-+]?\d+)?/g,No=new RegExp(ql.source,"g");function hy(i){return function(){return i}}function dy(i){return function(t){return i(t)+""}}function py(i,t){var e=ql.lastIndex=No.lastIndex=0,n,r,s,a=-1,o=[],l=[];for(i=i+"",t=t+"";(n=ql.exec(i))&&(r=No.exec(t));)(s=r.index)>e&&(s=t.slice(e,s),o[a]?o[a]+=s:o[++a]=s),(n=n[0])===(r=r[0])?o[a]?o[a]+=r:o[++a]=r:(o[++a]=null,l.push({i:a,x:pi(n,r)})),e=No.lastIndex;return e<t.length&&(s=t.slice(e),o[a]?o[a]+=s:o[++a]=s),o.length<2?l[0]?dy(l[0].x):hy(t):(t=l.length,function(c){for(var u=0,h;u<t;++u)o[(h=l[u]).i]=h.x(c);return o.join("")})}var _f=180/Math.PI,Yl={translateX:0,translateY:0,rotate:0,skewX:0,scaleX:1,scaleY:1};function yd(i,t,e,n,r,s){var a,o,l;return(a=Math.sqrt(i*i+t*t))&&(i/=a,t/=a),(l=i*e+t*n)&&(e-=i*l,n-=t*l),(o=Math.sqrt(e*e+n*n))&&(e/=o,n/=o,l/=o),i*n<t*e&&(i=-i,t=-t,l=-l,a=-a),{translateX:r,translateY:s,rotate:Math.atan2(t,i)*_f,skewX:Math.atan(l)*_f,scaleX:a,scaleY:o}}var na;function my(i){const t=new(typeof DOMMatrix=="function"?DOMMatrix:WebKitCSSMatrix)(i+"");return t.isIdentity?Yl:yd(t.a,t.b,t.c,t.d,t.e,t.f)}function _y(i){return i==null||(na||(na=document.createElementNS("http://www.w3.org/2000/svg","g")),na.setAttribute("transform",i),!(i=na.transform.baseVal.consolidate()))?Yl:(i=i.matrix,yd(i.a,i.b,i.c,i.d,i.e,i.f))}function Ed(i,t,e,n){function r(c){return c.length?c.pop()+" ":""}function s(c,u,h,f,d,_){if(c!==h||u!==f){var g=d.push("translate(",null,t,null,e);_.push({i:g-4,x:pi(c,h)},{i:g-2,x:pi(u,f)})}else(h||f)&&d.push("translate("+h+t+f+e)}function a(c,u,h,f){c!==u?(c-u>180?u+=360:u-c>180&&(c+=360),f.push({i:h.push(r(h)+"rotate(",null,n)-2,x:pi(c,u)})):u&&h.push(r(h)+"rotate("+u+n)}function o(c,u,h,f){c!==u?f.push({i:h.push(r(h)+"skewX(",null,n)-2,x:pi(c,u)}):u&&h.push(r(h)+"skewX("+u+n)}function l(c,u,h,f,d,_){if(c!==h||u!==f){var g=d.push(r(d)+"scale(",null,",",null,")");_.push({i:g-4,x:pi(c,h)},{i:g-2,x:pi(u,f)})}else(h!==1||f!==1)&&d.push(r(d)+"scale("+h+","+f+")")}return function(c,u){var h=[],f=[];return c=i(c),u=i(u),s(c.translateX,c.translateY,u.translateX,u.translateY,h,f),a(c.rotate,u.rotate,h,f),o(c.skewX,u.skewX,h,f),l(c.scaleX,c.scaleY,u.scaleX,u.scaleY,h,f),c=u=null,function(d){for(var _=-1,g=f.length,p;++_<g;)h[(p=f[_]).i]=p.x(d);return h.join("")}}}var gy=Ed(my,"px, ","px)","deg)"),xy=Ed(_y,", ",")",")"),Or=0,ts=0,Kr=0,Td=1e3,Pa,es,Da=0,ji=0,Ga=0,Ms=typeof performance=="object"&&performance.now?performance:Date,bd=typeof window=="object"&&window.requestAnimationFrame?window.requestAnimationFrame.bind(window):function(i){setTimeout(i,17)};function Ic(){return ji||(bd(vy),ji=Ms.now()+Ga)}function vy(){ji=0}function La(){this._call=this._time=this._next=null}La.prototype=Ad.prototype={constructor:La,restart:function(i,t,e){if(typeof i!="function")throw new TypeError("callback is not a function");e=(e==null?Ic():+e)+(t==null?0:+t),!this._next&&es!==this&&(es?es._next=this:Pa=this,es=this),this._call=i,this._time=e,$l()},stop:function(){this._call&&(this._call=null,this._time=1/0,$l())}};function Ad(i,t,e){var n=new La;return n.restart(i,t,e),n}function My(){Ic(),++Or;for(var i=Pa,t;i;)(t=ji-i._time)>=0&&i._call.call(void 0,t),i=i._next;--Or}function gf(){ji=(Da=Ms.now())+Ga,Or=ts=0;try{My()}finally{Or=0,yy(),ji=0}}function Sy(){var i=Ms.now(),t=i-Da;t>Td&&(Ga-=t,Da=i)}function yy(){for(var i,t=Pa,e,n=1/0;t;)t._call?(n>t._time&&(n=t._time),i=t,t=t._next):(e=t._next,t._next=null,t=i?i._next=e:Pa=e);es=i,$l(n)}function $l(i){if(!Or){ts&&(ts=clearTimeout(ts));var t=i-ji;t>24?(i<1/0&&(ts=setTimeout(gf,i-Ms.now()-Ga)),Kr&&(Kr=clearInterval(Kr))):(Kr||(Da=Ms.now(),Kr=setInterval(Sy,Td)),Or=1,bd(gf))}}function xf(i,t,e){var n=new La;return t=t==null?0:+t,n.restart(r=>{n.stop(),i(r+t)},t,e),n}var Ey=sd("start","end","cancel","interrupt"),Ty=[],wd=0,vf=1,Kl=2,pa=3,Mf=4,Zl=5,ma=6;function Ha(i,t,e,n,r,s){var a=i.__transition;if(!a)i.__transition={};else if(e in a)return;by(i,e,{name:t,index:n,group:r,on:Ey,tween:Ty,time:s.time,delay:s.delay,duration:s.duration,ease:s.ease,timer:null,state:wd})}function Uc(i,t){var e=vn(i,t);if(e.state>wd)throw new Error("too late; already scheduled");return e}function On(i,t){var e=vn(i,t);if(e.state>pa)throw new Error("too late; already running");return e}function vn(i,t){var e=i.__transition;if(!e||!(e=e[t]))throw new Error("transition not found");return e}function by(i,t,e){var n=i.__transition,r;n[t]=e,e.timer=Ad(s,0,e.time);function s(c){e.state=vf,e.timer.restart(a,e.delay,e.time),e.delay<=c&&a(c-e.delay)}function a(c){var u,h,f,d;if(e.state!==vf)return l();for(u in n)if(d=n[u],d.name===e.name){if(d.state===pa)return xf(a);d.state===Mf?(d.state=ma,d.timer.stop(),d.on.call("interrupt",i,i.__data__,d.index,d.group),delete n[u]):+u<t&&(d.state=ma,d.timer.stop(),d.on.call("cancel",i,i.__data__,d.index,d.group),delete n[u])}if(xf(function(){e.state===pa&&(e.state=Mf,e.timer.restart(o,e.delay,e.time),o(c))}),e.state=Kl,e.on.call("start",i,i.__data__,e.index,e.group),e.state===Kl){for(e.state=pa,r=new Array(f=e.tween.length),u=0,h=-1;u<f;++u)(d=e.tween[u].value.call(i,i.__data__,e.index,e.group))&&(r[++h]=d);r.length=h+1}}function o(c){for(var u=c<e.duration?e.ease.call(null,c/e.duration):(e.timer.restart(l),e.state=Zl,1),h=-1,f=r.length;++h<f;)r[h].call(i,u);e.state===Zl&&(e.on.call("end",i,i.__data__,e.index,e.group),l())}function l(){e.state=ma,e.timer.stop(),delete n[t];for(var c in n)return;delete i.__transition}}function Ay(i,t){var e=i.__transition,n,r,s=!0,a;if(e){t=t==null?null:t+"";for(a in e){if((n=e[a]).name!==t){s=!1;continue}r=n.state>Kl&&n.state<Zl,n.state=ma,n.timer.stop(),n.on.call(r?"interrupt":"cancel",i,i.__data__,n.index,n.group),delete e[a]}s&&delete i.__transition}}function wy(i){return this.each(function(){Ay(this,i)})}function Ry(i,t){var e,n;return function(){var r=On(this,i),s=r.tween;if(s!==e){n=e=s;for(var a=0,o=n.length;a<o;++a)if(n[a].name===t){n=n.slice(),n.splice(a,1);break}}r.tween=n}}function Cy(i,t,e){var n,r;if(typeof e!="function")throw new Error;return function(){var s=On(this,i),a=s.tween;if(a!==n){r=(n=a).slice();for(var o={name:t,value:e},l=0,c=r.length;l<c;++l)if(r[l].name===t){r[l]=o;break}l===c&&r.push(o)}s.tween=r}}function Py(i,t){var e=this._id;if(i+="",arguments.length<2){for(var n=vn(this.node(),e).tween,r=0,s=n.length,a;r<s;++r)if((a=n[r]).name===i)return a.value;return null}return this.each((t==null?Ry:Cy)(e,i,t))}function Nc(i,t,e){var n=i._id;return i.each(function(){var r=On(this,n);(r.value||(r.value={}))[t]=e.apply(this,arguments)}),function(r){return vn(r,n).value[t]}}function Rd(i,t){var e;return(typeof t=="number"?pi:t instanceof vs?mf:(e=vs(t))?(t=e,mf):py)(i,t)}function Dy(i){return function(){this.removeAttribute(i)}}function Ly(i){return function(){this.removeAttributeNS(i.space,i.local)}}function Iy(i,t,e){var n,r=e+"",s;return function(){var a=this.getAttribute(i);return a===r?null:a===n?s:s=t(n=a,e)}}function Uy(i,t,e){var n,r=e+"",s;return function(){var a=this.getAttributeNS(i.space,i.local);return a===r?null:a===n?s:s=t(n=a,e)}}function Ny(i,t,e){var n,r,s;return function(){var a,o=e(this),l;return o==null?void this.removeAttribute(i):(a=this.getAttribute(i),l=o+"",a===l?null:a===n&&l===r?s:(r=l,s=t(n=a,o)))}}function Fy(i,t,e){var n,r,s;return function(){var a,o=e(this),l;return o==null?void this.removeAttributeNS(i.space,i.local):(a=this.getAttributeNS(i.space,i.local),l=o+"",a===l?null:a===n&&l===r?s:(r=l,s=t(n=a,o)))}}function Oy(i,t){var e=Va(i),n=e==="transform"?xy:Rd;return this.attrTween(i,typeof t=="function"?(e.local?Fy:Ny)(e,n,Nc(this,"attr."+i,t)):t==null?(e.local?Ly:Dy)(e):(e.local?Uy:Iy)(e,n,t))}function By(i,t){return function(e){this.setAttribute(i,t.call(this,e))}}function ky(i,t){return function(e){this.setAttributeNS(i.space,i.local,t.call(this,e))}}function zy(i,t){var e,n;function r(){var s=t.apply(this,arguments);return s!==n&&(e=(n=s)&&ky(i,s)),e}return r._value=t,r}function Vy(i,t){var e,n;function r(){var s=t.apply(this,arguments);return s!==n&&(e=(n=s)&&By(i,s)),e}return r._value=t,r}function Gy(i,t){var e="attr."+i;if(arguments.length<2)return(e=this.tween(e))&&e._value;if(t==null)return this.tween(e,null);if(typeof t!="function")throw new Error;var n=Va(i);return this.tween(e,(n.local?zy:Vy)(n,t))}function Hy(i,t){return function(){Uc(this,i).delay=+t.apply(this,arguments)}}function Wy(i,t){return t=+t,function(){Uc(this,i).delay=t}}function Xy(i){var t=this._id;return arguments.length?this.each((typeof i=="function"?Hy:Wy)(t,i)):vn(this.node(),t).delay}function qy(i,t){return function(){On(this,i).duration=+t.apply(this,arguments)}}function Yy(i,t){return t=+t,function(){On(this,i).duration=t}}function $y(i){var t=this._id;return arguments.length?this.each((typeof i=="function"?qy:Yy)(t,i)):vn(this.node(),t).duration}function Ky(i,t){if(typeof t!="function")throw new Error;return function(){On(this,i).ease=t}}function Zy(i){var t=this._id;return arguments.length?this.each(Ky(t,i)):vn(this.node(),t).ease}function Jy(i,t){return function(){var e=t.apply(this,arguments);if(typeof e!="function")throw new Error;On(this,i).ease=e}}function jy(i){if(typeof i!="function")throw new Error;return this.each(Jy(this._id,i))}function Qy(i){typeof i!="function"&&(i=ld(i));for(var t=this._groups,e=t.length,n=new Array(e),r=0;r<e;++r)for(var s=t[r],a=s.length,o=n[r]=[],l,c=0;c<a;++c)(l=s[c])&&i.call(l,l.__data__,c,s)&&o.push(l);return new ri(n,this._parents,this._name,this._id)}function tE(i){if(i._id!==this._id)throw new Error;for(var t=this._groups,e=i._groups,n=t.length,r=e.length,s=Math.min(n,r),a=new Array(n),o=0;o<s;++o)for(var l=t[o],c=e[o],u=l.length,h=a[o]=new Array(u),f,d=0;d<u;++d)(f=l[d]||c[d])&&(h[d]=f);for(;o<n;++o)a[o]=t[o];return new ri(a,this._parents,this._name,this._id)}function eE(i){return(i+"").trim().split(/^|\s+/).every(function(t){var e=t.indexOf(".");return e>=0&&(t=t.slice(0,e)),!t||t==="start"})}function nE(i,t,e){var n,r,s=eE(t)?Uc:On;return function(){var a=s(this,i),o=a.on;o!==n&&(r=(n=o).copy()).on(t,e),a.on=r}}function iE(i,t){var e=this._id;return arguments.length<2?vn(this.node(),e).on.on(i):this.each(nE(e,i,t))}function rE(i){return function(){var t=this.parentNode;for(var e in this.__transition)if(+e!==i)return;t&&t.removeChild(this)}}function sE(){return this.on("end.remove",rE(this._id))}function aE(i){var t=this._name,e=this._id;typeof i!="function"&&(i=Pc(i));for(var n=this._groups,r=n.length,s=new Array(r),a=0;a<r;++a)for(var o=n[a],l=o.length,c=s[a]=new Array(l),u,h,f=0;f<l;++f)(u=o[f])&&(h=i.call(u,u.__data__,f,o))&&("__data__"in u&&(h.__data__=u.__data__),c[f]=h,Ha(c[f],t,e,f,c,vn(u,e)));return new ri(s,this._parents,t,e)}function oE(i){var t=this._name,e=this._id;typeof i!="function"&&(i=od(i));for(var n=this._groups,r=n.length,s=[],a=[],o=0;o<r;++o)for(var l=n[o],c=l.length,u,h=0;h<c;++h)if(u=l[h]){for(var f=i.call(u,u.__data__,h,l),d,_=vn(u,e),g=0,p=f.length;g<p;++g)(d=f[g])&&Ha(d,t,e,g,f,_);s.push(f),a.push(u)}return new ri(s,a,t,e)}var lE=As.prototype.constructor;function cE(){return new lE(this._groups,this._parents)}function uE(i,t){var e,n,r;return function(){var s=Fr(this,i),a=(this.style.removeProperty(i),Fr(this,i));return s===a?null:s===e&&a===n?r:r=t(e=s,n=a)}}function Cd(i){return function(){this.style.removeProperty(i)}}function fE(i,t,e){var n,r=e+"",s;return function(){var a=Fr(this,i);return a===r?null:a===n?s:s=t(n=a,e)}}function hE(i,t,e){var n,r,s;return function(){var a=Fr(this,i),o=e(this),l=o+"";return o==null&&(l=o=(this.style.removeProperty(i),Fr(this,i))),a===l?null:a===n&&l===r?s:(r=l,s=t(n=a,o))}}function dE(i,t){var e,n,r,s="style."+t,a="end."+s,o;return function(){var l=On(this,i),c=l.on,u=l.value[s]==null?o||(o=Cd(t)):void 0;(c!==e||r!==u)&&(n=(e=c).copy()).on(a,r=u),l.on=n}}function pE(i,t,e){var n=(i+="")=="transform"?gy:Rd;return t==null?this.styleTween(i,uE(i,n)).on("end.style."+i,Cd(i)):typeof t=="function"?this.styleTween(i,hE(i,n,Nc(this,"style."+i,t))).each(dE(this._id,i)):this.styleTween(i,fE(i,n,t),e).on("end.style."+i,null)}function mE(i,t,e){return function(n){this.style.setProperty(i,t.call(this,n),e)}}function _E(i,t,e){var n,r;function s(){var a=t.apply(this,arguments);return a!==r&&(n=(r=a)&&mE(i,a,e)),n}return s._value=t,s}function gE(i,t,e){var n="style."+(i+="");if(arguments.length<2)return(n=this.tween(n))&&n._value;if(t==null)return this.tween(n,null);if(typeof t!="function")throw new Error;return this.tween(n,_E(i,t,e??""))}function xE(i){return function(){this.textContent=i}}function vE(i){return function(){var t=i(this);this.textContent=t??""}}function ME(i){return this.tween("text",typeof i=="function"?vE(Nc(this,"text",i)):xE(i==null?"":i+""))}function SE(i){return function(t){this.textContent=i.call(this,t)}}function yE(i){var t,e;function n(){var r=i.apply(this,arguments);return r!==e&&(t=(e=r)&&SE(r)),t}return n._value=i,n}function EE(i){var t="text";if(arguments.length<1)return(t=this.tween(t))&&t._value;if(i==null)return this.tween(t,null);if(typeof i!="function")throw new Error;return this.tween(t,yE(i))}function TE(){for(var i=this._name,t=this._id,e=Pd(),n=this._groups,r=n.length,s=0;s<r;++s)for(var a=n[s],o=a.length,l,c=0;c<o;++c)if(l=a[c]){var u=vn(l,t);Ha(l,i,e,c,a,{time:u.time+u.delay+u.duration,delay:0,duration:u.duration,ease:u.ease})}return new ri(n,this._parents,i,e)}function bE(){var i,t,e=this,n=e._id,r=e.size();return new Promise(function(s,a){var o={value:a},l={value:function(){--r===0&&s()}};e.each(function(){var c=On(this,n),u=c.on;u!==i&&(t=(i=u).copy(),t._.cancel.push(o),t._.interrupt.push(o),t._.end.push(l)),c.on=t}),r===0&&s()})}var AE=0;function ri(i,t,e,n){this._groups=i,this._parents=t,this._name=e,this._id=n}function Pd(){return++AE}var Xn=As.prototype;ri.prototype={constructor:ri,select:aE,selectAll:oE,selectChild:Xn.selectChild,selectChildren:Xn.selectChildren,filter:Qy,merge:tE,selection:cE,transition:TE,call:Xn.call,nodes:Xn.nodes,node:Xn.node,size:Xn.size,empty:Xn.empty,each:Xn.each,on:iE,attr:Oy,attrTween:Gy,style:pE,styleTween:gE,text:ME,textTween:EE,remove:sE,tween:Py,delay:Xy,duration:$y,ease:Zy,easeVarying:jy,end:bE,[Symbol.iterator]:Xn[Symbol.iterator]};function wE(i){return((i*=2)<=1?i*i*i:(i-=2)*i*i+2)/2}var RE={time:null,delay:0,duration:250,ease:wE};function CE(i,t){for(var e;!(e=i.__transition)||!(e=e[t]);)if(!(i=i.parentNode))throw new Error(`transition ${t} not found`);return e}function PE(i){var t,e;i instanceof ri?(t=i._id,i=i._name):(t=Pd(),(e=RE).time=Ic(),i=i==null?null:i+"");for(var n=this._groups,r=n.length,s=0;s<r;++s)for(var a=n[s],o=a.length,l,c=0;c<o;++c)(l=a[c])&&Ha(l,i,t,c,a,e||CE(l,t));return new ri(n,this._parents,i,t)}As.prototype.interrupt=wy;As.prototype.transition=PE;function ns(i,t,e){this.k=i,this.x=t,this.y=e}ns.prototype={constructor:ns,scale:function(i){return i===1?this:new ns(this.k*i,this.x,this.y)},translate:function(i,t){return i===0&t===0?this:new ns(this.k,this.x+this.k*i,this.y+this.k*t)},apply:function(i){return[i[0]*this.k+this.x,i[1]*this.k+this.y]},applyX:function(i){return i*this.k+this.x},applyY:function(i){return i*this.k+this.y},invert:function(i){return[(i[0]-this.x)/this.k,(i[1]-this.y)/this.k]},invertX:function(i){return(i-this.x)/this.k},invertY:function(i){return(i-this.y)/this.k},rescaleX:function(i){return i.copy().domain(i.range().map(this.invertX,this).map(i.invert,i))},rescaleY:function(i){return i.copy().domain(i.range().map(this.invertY,this).map(i.invert,i))},toString:function(){return"translate("+this.x+","+this.y+") scale("+this.k+")"}};ns.prototype;function Sf(i,t){let e;if(t===void 0)for(const n of i)n!=null&&(e<n||e===void 0&&n>=n)&&(e=n);else{let n=-1;for(let r of i)(r=t(r,++n,i))!=null&&(e<r||e===void 0&&r>=r)&&(e=r)}return e}function DE(i,t){let e;if(t===void 0)for(const n of i)n!=null&&(e>n||e===void 0&&n>=n)&&(e=n);else{let n=-1;for(let r of i)(r=t(r,++n,i))!=null&&(e>r||e===void 0&&r>=r)&&(e=r)}return e}function Fo(i,t){let e=0;if(t===void 0)for(let n of i)(n=+n)&&(e+=n);else{let n=-1;for(let r of i)(r=+t(r,++n,i))&&(e+=r)}return e}function LE(i,t){return i.sourceLinks.length?i.depth:t-1}function ia(i){return function(){return i}}function yf(i,t){return Ia(i.source,t.source)||i.index-t.index}function Ef(i,t){return Ia(i.target,t.target)||i.index-t.index}function Ia(i,t){return i.y0-t.y0}function Oo(i){return i.value}function IE(i){return i.index}function UE(i){return i.nodes}function NE(i){return i.links}function Tf(i,t){const e=i.get(t);if(!e)throw new Error("missing: "+t);return e}function bf({nodes:i}){for(const t of i){let e=t.y0,n=e;for(const r of t.sourceLinks)r.y0=e+r.width/2,e+=r.width;for(const r of t.targetLinks)r.y1=n+r.width/2,n+=r.width}}function FE(){let i=0,t=0,e=1,n=1,r=24,s=8,a,o=IE,l=LE,c,u,h=UE,f=NE,d=6;function _(){const C={nodes:h.apply(null,arguments),links:f.apply(null,arguments)};return g(C),p(C),m(C),M(C),b(C),bf(C),C}_.update=function(C){return bf(C),C},_.nodeId=function(C){return arguments.length?(o=typeof C=="function"?C:ia(C),_):o},_.nodeAlign=function(C){return arguments.length?(l=typeof C=="function"?C:ia(C),_):l},_.nodeSort=function(C){return arguments.length?(c=C,_):c},_.nodeWidth=function(C){return arguments.length?(r=+C,_):r},_.nodePadding=function(C){return arguments.length?(s=a=+C,_):s},_.nodes=function(C){return arguments.length?(h=typeof C=="function"?C:ia(C),_):h},_.links=function(C){return arguments.length?(f=typeof C=="function"?C:ia(C),_):f},_.linkSort=function(C){return arguments.length?(u=C,_):u},_.size=function(C){return arguments.length?(i=t=0,e=+C[0],n=+C[1],_):[e-i,n-t]},_.extent=function(C){return arguments.length?(i=+C[0][0],e=+C[1][0],t=+C[0][1],n=+C[1][1],_):[[i,t],[e,n]]},_.iterations=function(C){return arguments.length?(d=+C,_):d};function g({nodes:C,links:L}){for(const[z,O]of C.entries())O.index=z,O.sourceLinks=[],O.targetLinks=[];const P=new Map(C.map((z,O)=>[o(z,O,C),z]));for(const[z,O]of L.entries()){O.index=z;let{source:J,target:Q}=O;typeof J!="object"&&(J=O.source=Tf(P,J)),typeof Q!="object"&&(Q=O.target=Tf(P,Q)),J.sourceLinks.push(O),Q.targetLinks.push(O)}if(u!=null)for(const{sourceLinks:z,targetLinks:O}of C)z.sort(u),O.sort(u)}function p({nodes:C}){for(const L of C)L.value=L.fixedValue===void 0?Math.max(Fo(L.sourceLinks,Oo),Fo(L.targetLinks,Oo)):L.fixedValue}function m({nodes:C}){const L=C.length;let P=new Set(C),z=new Set,O=0;for(;P.size;){for(const J of P){J.depth=O;for(const{target:Q}of J.sourceLinks)z.add(Q)}if(++O>L)throw new Error("circular link");P=z,z=new Set}}function M({nodes:C}){const L=C.length;let P=new Set(C),z=new Set,O=0;for(;P.size;){for(const J of P){J.height=O;for(const{source:Q}of J.targetLinks)z.add(Q)}if(++O>L)throw new Error("circular link");P=z,z=new Set}}function T({nodes:C}){const L=Sf(C,O=>O.depth)+1,P=(e-i-r)/(L-1),z=new Array(L);for(const O of C){const J=Math.max(0,Math.min(L-1,Math.floor(l.call(null,O,L))));O.layer=J,O.x0=i+J*P,O.x1=O.x0+r,z[J]?z[J].push(O):z[J]=[O]}if(c)for(const O of z)O.sort(c);return z}function S(C){const L=DE(C,P=>(n-t-(P.length-1)*a)/Fo(P,Oo));for(const P of C){let z=t;for(const O of P){O.y0=z,O.y1=z+O.value*L,z=O.y1+a;for(const J of O.sourceLinks)J.width=J.value*L}z=(n-z+a)/(P.length+1);for(let O=0;O<P.length;++O){const J=P[O];J.y0+=z*(O+1),J.y1+=z*(O+1)}B(P)}}function b(C){const L=T(C);a=Math.min(s,(n-t)/(Sf(L,P=>P.length)-1)),S(L);for(let P=0;P<d;++P){const z=Math.pow(.99,P),O=Math.max(1-z,(P+1)/d);R(L,z,O),A(L,z,O)}}function A(C,L,P){for(let z=1,O=C.length;z<O;++z){const J=C[z];for(const Q of J){let st=0,bt=0;for(const{source:Ft,value:K}of Q.targetLinks){let nt=K*(Q.layer-Ft.layer);st+=k(Ft,Q)*nt,bt+=nt}if(!(bt>0))continue;let Ut=(st/bt-Q.y0)*L;Q.y0+=Ut,Q.y1+=Ut,D(Q)}c===void 0&&J.sort(Ia),x(J,P)}}function R(C,L,P){for(let z=C.length,O=z-2;O>=0;--O){const J=C[O];for(const Q of J){let st=0,bt=0;for(const{target:Ft,value:K}of Q.sourceLinks){let nt=K*(Ft.layer-Q.layer);st+=X(Q,Ft)*nt,bt+=nt}if(!(bt>0))continue;let Ut=(st/bt-Q.y0)*L;Q.y0+=Ut,Q.y1+=Ut,D(Q)}c===void 0&&J.sort(Ia),x(J,P)}}function x(C,L){const P=C.length>>1,z=C[P];G(C,z.y0-a,P-1,L),y(C,z.y1+a,P+1,L),G(C,n,C.length-1,L),y(C,t,0,L)}function y(C,L,P,z){for(;P<C.length;++P){const O=C[P],J=(L-O.y0)*z;J>1e-6&&(O.y0+=J,O.y1+=J),L=O.y1+a}}function G(C,L,P,z){for(;P>=0;--P){const O=C[P],J=(O.y1-L)*z;J>1e-6&&(O.y0-=J,O.y1-=J),L=O.y0-a}}function D({sourceLinks:C,targetLinks:L}){if(u===void 0){for(const{source:{sourceLinks:P}}of L)P.sort(Ef);for(const{target:{targetLinks:P}}of C)P.sort(yf)}}function B(C){if(u===void 0)for(const{sourceLinks:L,targetLinks:P}of C)L.sort(Ef),P.sort(yf)}function k(C,L){let P=C.y0-(C.sourceLinks.length-1)*a/2;for(const{target:z,width:O}of C.sourceLinks){if(z===L)break;P+=O+a}for(const{source:z,width:O}of L.targetLinks){if(z===C)break;P-=O}return P}function X(C,L){let P=L.y0-(L.targetLinks.length-1)*a/2;for(const{source:z,width:O}of L.targetLinks){if(z===C)break;P+=O+a}for(const{target:z,width:O}of C.sourceLinks){if(z===L)break;P-=O}return P}return _}var Jl=Math.PI,jl=2*Jl,ki=1e-6,OE=jl-ki;function Ql(){this._x0=this._y0=this._x1=this._y1=null,this._=""}function Dd(){return new Ql}Ql.prototype=Dd.prototype={constructor:Ql,moveTo:function(i,t){this._+="M"+(this._x0=this._x1=+i)+","+(this._y0=this._y1=+t)},closePath:function(){this._x1!==null&&(this._x1=this._x0,this._y1=this._y0,this._+="Z")},lineTo:function(i,t){this._+="L"+(this._x1=+i)+","+(this._y1=+t)},quadraticCurveTo:function(i,t,e,n){this._+="Q"+ +i+","+ +t+","+(this._x1=+e)+","+(this._y1=+n)},bezierCurveTo:function(i,t,e,n,r,s){this._+="C"+ +i+","+ +t+","+ +e+","+ +n+","+(this._x1=+r)+","+(this._y1=+s)},arcTo:function(i,t,e,n,r){i=+i,t=+t,e=+e,n=+n,r=+r;var s=this._x1,a=this._y1,o=e-i,l=n-t,c=s-i,u=a-t,h=c*c+u*u;if(r<0)throw new Error("negative radius: "+r);if(this._x1===null)this._+="M"+(this._x1=i)+","+(this._y1=t);else if(h>ki)if(!(Math.abs(u*o-l*c)>ki)||!r)this._+="L"+(this._x1=i)+","+(this._y1=t);else{var f=e-s,d=n-a,_=o*o+l*l,g=f*f+d*d,p=Math.sqrt(_),m=Math.sqrt(h),M=r*Math.tan((Jl-Math.acos((_+h-g)/(2*p*m)))/2),T=M/m,S=M/p;Math.abs(T-1)>ki&&(this._+="L"+(i+T*c)+","+(t+T*u)),this._+="A"+r+","+r+",0,0,"+ +(u*f>c*d)+","+(this._x1=i+S*o)+","+(this._y1=t+S*l)}},arc:function(i,t,e,n,r,s){i=+i,t=+t,e=+e,s=!!s;var a=e*Math.cos(n),o=e*Math.sin(n),l=i+a,c=t+o,u=1^s,h=s?n-r:r-n;if(e<0)throw new Error("negative radius: "+e);this._x1===null?this._+="M"+l+","+c:(Math.abs(this._x1-l)>ki||Math.abs(this._y1-c)>ki)&&(this._+="L"+l+","+c),e&&(h<0&&(h=h%jl+jl),h>OE?this._+="A"+e+","+e+",0,1,"+u+","+(i-a)+","+(t-o)+"A"+e+","+e+",0,1,"+u+","+(this._x1=l)+","+(this._y1=c):h>ki&&(this._+="A"+e+","+e+",0,"+ +(h>=Jl)+","+u+","+(this._x1=i+e*Math.cos(r))+","+(this._y1=t+e*Math.sin(r))))},rect:function(i,t,e,n){this._+="M"+(this._x0=this._x1=+i)+","+(this._y0=this._y1=+t)+"h"+ +e+"v"+ +n+"h"+-e+"Z"},toString:function(){return this._}};function Af(i){return function(){return i}}function BE(i){return i[0]}function kE(i){return i[1]}var zE=Array.prototype.slice;function VE(i){return i.source}function GE(i){return i.target}function HE(i){var t=VE,e=GE,n=BE,r=kE,s=null;function a(){var o,l=zE.call(arguments),c=t.apply(this,l),u=e.apply(this,l);if(s||(s=o=Dd()),i(s,+n.apply(this,(l[0]=c,l)),+r.apply(this,l),+n.apply(this,(l[0]=u,l)),+r.apply(this,l)),o)return s=null,o+""||null}return a.source=function(o){return arguments.length?(t=o,a):t},a.target=function(o){return arguments.length?(e=o,a):e},a.x=function(o){return arguments.length?(n=typeof o=="function"?o:Af(+o),a):n},a.y=function(o){return arguments.length?(r=typeof o=="function"?o:Af(+o),a):r},a.context=function(o){return arguments.length?(s=o??null,a):s},a}function WE(i,t,e,n,r){i.moveTo(t,e),i.bezierCurveTo(t=(t+n)/2,e,t,r,n,r)}function XE(){return HE(WE)}function qE(i){return[i.source.x1,i.y0]}function YE(i){return[i.target.x0,i.y1]}function $E(){return XE().source(qE).target(YE)}const KE=[{id:"sankey-one",data:{nodes:[{id:"control_hallucination",name:"Hallucination checks (6)",stage:"Baseline",note:"Raw suite=hallucination; total=6; pass=6; fail=0",evidence:["grounded_invoice_total","grounded_policy_join","grounded_guardrails"]},{id:"control_style",name:"Style checks (6)",stage:"Baseline",note:"Raw suite=style; total=6; pass=6; fail=0",evidence:["concise_playful_precision","followup_tone_continuity","structured_strategy_answer"]},{id:"control_retrieval",name:"Retrieval checks (12)",stage:"Baseline",note:"Raw suite=retrieval; total=12; pass=12; fail=0",evidence:["aurora_lattice","cedar_loop","delta_forge"]},{id:"control_file_search",name:"File-search checks (5)",stage:"Baseline",note:"Raw suite=file-search; total=5; pass=5; fail=0",evidence:["ocr_signal_chain","ocr_lineage_guard","pdf_invoice_totals"]},{id:"bridge_spine_one",name:"Bridge (Polinko Beta 1.0) (29)",stage:"Bridge (Polinko Beta 1.0)",note:"Raw baseline suites collapsed into bridge. Bridge suite (ocr) observed total=6; pass=6; fail=0.",evidence:["ocr_verbatim_smoke","ocr_normalized_smoke","ocr_crossout_replacement_order"]}],links:[{id:"control_to_bridge_hallucination",source:"control_hallucination",target:"bridge_spine_one",value:6,note:"Hallucination checks raw contribution into bridge."},{id:"control_to_bridge_style",source:"control_style",target:"bridge_spine_one",value:6,note:"Style checks raw contribution into bridge."},{id:"control_to_bridge_retrieval",source:"control_retrieval",target:"bridge_spine_one",value:12,note:"Retrieval checks raw contribution into bridge."},{id:"control_to_bridge_file_search",source:"control_file_search",target:"bridge_spine_one",value:5,note:"File-search checks raw contribution into bridge."}]}},{id:"sankey-two",data:{nodes:[{id:"bridge_spine_two",name:"Bridge (Polinko Beta 1.0) (15)",stage:"Bridge (Polinko Beta 1.0)",note:"Input bridge for ocr_transcript_stability; raw total=15; pass=15; fail=0",evidence:["tx-68f91bcc-006","tx-695bf82d-014","tx-694aef69-009"]},{id:"beta2_lane_typed",name:"Typed lane (7)",stage:"Polinko Beta 2.0",note:"Raw lane=typed; total=7; pass=7; fail=0"},{id:"beta2_lane_handwriting",name:"Handwriting lane (5)",stage:"Polinko Beta 2.0",note:"Raw lane=handwriting; total=5; pass=5; fail=0"},{id:"beta2_lane_illustration",name:"Illustration lane (3)",stage:"Polinko Beta 2.0",note:"Raw lane=illustration; total=3; pass=3; fail=0"}],links:[{id:"bridge_to_beta2_typed",source:"bridge_spine_two",target:"beta2_lane_typed",value:7,note:"Bridge flow into Beta 2.0 typed lane."},{id:"bridge_to_beta2_handwriting",source:"bridge_spine_two",target:"beta2_lane_handwriting",value:5,note:"Bridge flow into Beta 2.0 handwriting lane."},{id:"bridge_to_beta2_illustration",source:"bridge_spine_two",target:"beta2_lane_illustration",value:3,note:"Bridge flow into Beta 2.0 illustration lane."}]}}],ZE={sankeys:KE},JE=["hero","intro","pipeline-one","sankey-one","sankey-two","pipeline-two","conclusion","about"];function jE(i){return!i||!Array.isArray(i.sankeys)?[]:i.sankeys.filter(t=>t&&typeof t.id=="string"&&t.data).map(t=>({id:t.id,data:{nodes:Array.isArray(t.data.nodes)?t.data.nodes:[],links:Array.isArray(t.data.links)?t.data.links:[]}}))}const QE=jE(ZE);function tT(){const i=document.getElementById("webgl-stage");if(!(i instanceof HTMLCanvasElement))return()=>{};const t=new t_;t.background=new Zt(16645629);const e=new ln(55,window.innerWidth/window.innerHeight,.1,100);e.position.z=3.2;const n=new pM({canvas:i,antialias:!0,alpha:!1});n.setPixelRatio(Math.min(window.devicePixelRatio,2)),n.setSize(window.innerWidth,window.innerHeight);const r=new bs(5.4,5.4,1,1),s=new Cc({color:16316399}),a=new Nn(r,s);a.position.z=-.25,t.add(a);const o=()=>n.render(t,e);o();const l=()=>{e.aspect=window.innerWidth/window.innerHeight,e.updateProjectionMatrix(),n.setSize(window.innerWidth,window.innerHeight),o()};return window.addEventListener("resize",l),()=>{window.removeEventListener("resize",l),r.dispose(),s.dispose(),n.dispose()}}function eT(){const i=document.querySelector(".board");if(!(i instanceof HTMLElement))return()=>{};const t=JE.map(u=>document.getElementById(u)).filter(Boolean);let e=0,n=!1,r=0;const s=()=>{t.forEach((u,h)=>{u.classList.toggle("is-active",h===e)})},a=(u,h=!1)=>{const f=Math.max(0,Math.min(u,t.length-1));if(f===e)return;e=f;const d=t[e];if(!(d instanceof HTMLElement))return;s();const _=h?0:.88;h||(n=!0),ds.to(i,{x:-d.offsetLeft,y:-d.offsetTop,duration:_,ease:"power3.inOut",onComplete:()=>{n=!1},onInterrupt:()=>{n=!1},overwrite:"auto"}),window.dispatchEvent(new CustomEvent("polinko:section-change",{detail:{id:d.id,index:e}}))},o=u=>{u.preventDefault();const h=performance.now();if(h<r||n||Math.abs(u.deltaY)<8)return;r=h+420;const f=u.deltaY>0?1:-1;a(e+f)},l=u=>{n||((u.key==="ArrowDown"||u.key==="ArrowRight"||u.key==="PageDown")&&(u.preventDefault(),a(e+1)),(u.key==="ArrowUp"||u.key==="ArrowLeft"||u.key==="PageUp")&&(u.preventDefault(),a(e-1)))},c=()=>a(e,!0);return window.addEventListener("wheel",o,{passive:!1}),window.addEventListener("keydown",l),window.addEventListener("resize",c),ds.fromTo(".block",{opacity:0,scale:.985},{opacity:1,scale:1,duration:.66,ease:"power2.out",stagger:.045}),a(0,!0),()=>{window.removeEventListener("wheel",o),window.removeEventListener("keydown",l),window.removeEventListener("resize",c)}}function nT(i){return{nodes:i.nodes.map(t=>({...t})),links:i.links.map(t=>({...t}))}}function iT(){const i=[];return QE.forEach(t=>{const e=document.querySelector(`.sankey-chart-wrap[data-sankey-id="${t.id}"]`);if(!(e instanceof HTMLElement))return;const n=e.querySelector(".sankey-chart");if(!(n instanceof SVGElement))return;let r=null,s=null,a=null;const o=d=>{if(!r||!s||!a)return;const _=new Set,g=new Set;if((d==null?void 0:d.type)==="node")_.add(d.id),r.links.forEach(p=>{(p.source.id===d.id||p.target.id===d.id)&&(g.add(p.id),_.add(p.source.id),_.add(p.target.id))});else if((d==null?void 0:d.type)==="link"){const p=r.links.find(m=>m.id===d.id);p&&(g.add(p.id),_.add(p.source.id),_.add(p.target.id))}s.selectAll("rect").classed("is-active",p=>_.has(p.id)).classed("is-dim",p=>_.size>0&&!_.has(p.id)),a.classed("is-active",p=>g.has(p.id)).classed("is-dim",p=>g.size>0&&!g.has(p.id))},l=d=>{o({type:"node",id:d.id})},c=d=>{o({type:"link",id:d.id})},u=()=>{o(null)},h=()=>{const d=e.getBoundingClientRect(),_=Math.max(1,Math.floor(d.width)),g=Math.max(1,Math.floor(d.height)),m=e.closest(".sankey-shell-full")?{top:0,right:0,bottom:0,left:0}:{top:20,right:16,bottom:16,left:16},M=ZS(n);M.selectAll("*").remove(),M.attr("viewBox",`0 0 ${_} ${g}`),M.attr("preserveAspectRatio","xMidYMid meet"),r=FE().nodeId(S=>S.id).nodeWidth(18).nodePadding(20).extent([[m.left,m.top],[_-m.right,g-m.bottom]])(nT(t.data)),a=M.append("g").attr("fill","none").selectAll("path").data(r.links).join("path").attr("class","sankey-link-path").attr("d",$E()).attr("stroke-width",S=>Math.max(2,S.width)).on("mouseenter",(S,b)=>c(b)).on("mouseleave",()=>u()),s=M.append("g").selectAll("g").data(r.nodes).join("g").on("mouseenter",(S,b)=>l(b)).on("mouseleave",()=>u()),s.append("rect").attr("class","sankey-node-rect").attr("x",S=>S.x0).attr("y",S=>S.y0).attr("width",S=>Math.max(1,S.x1-S.x0)).attr("height",S=>Math.max(1,S.y1-S.y0)),s.append("text").attr("class","sankey-node-label").attr("x",S=>S.x0<_/2?S.x1+8:S.x0-8).attr("y",S=>(S.y0+S.y1)/2).attr("dy","0.35em").attr("text-anchor",S=>S.x0<_/2?"start":"end").text(S=>S.name),u()},f=new ResizeObserver(()=>h());f.observe(e),h(),i.push(()=>{f.disconnect()})}),()=>{i.forEach(t=>t())}}function rT(){const i=Array.from(document.querySelectorAll(".morph-stage")),t=document.querySelector(".morph-replay");if(!(t instanceof HTMLButtonElement)||i.length===0)return()=>{};const e=["baseline","bridge","beta2"];let n=!1,r=[];const s=c=>{i.forEach(u=>{u.classList.toggle("active",u.getAttribute("data-stage")===c)})},a=()=>{r.forEach(c=>c.kill()),r=[]},o=()=>{n&&a(),n=!0,e.forEach((c,u)=>{const h=ds.delayedCall(u*.55,()=>s(c));r.push(h)}),r.push(ds.delayedCall(e.length*.55+.05,()=>{n=!1}))},l=c=>{var u;((u=c.detail)==null?void 0:u.id)==="conclusion"&&o()};return t.addEventListener("click",o),window.addEventListener("polinko:section-change",l),s("baseline"),()=>{t.removeEventListener("click",o),window.removeEventListener("polinko:section-change",l),a()}}const sT=tT(),aT=eT(),oT=iT(),lT=rT();window.addEventListener("beforeunload",()=>{sT(),aT(),oT(),lT()});
