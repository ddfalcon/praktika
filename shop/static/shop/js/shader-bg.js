/* Фоновый дым на весь сайт — WebGL2-шейдер.
   Основан на «clouds/fbm»-шейдере (Matthias Hurrle), но без светящихся
   точек-«комет»: оставлен только клубящийся дым, перекрашенный в палитру сайта. */
(function () {
  var canvas = document.getElementById('siteGlow');
  if (!canvas) return;

  var gl = canvas.getContext('webgl2', { antialias: false, alpha: false });
  if (!gl) return; // нет WebGL2 — остаётся обычный светлый фон страницы

  var vertSrc = '#version 300 es\n' +
    'precision highp float;\n' +
    'in vec4 position;\n' +
    'void main(){gl_Position=position;}';

  var fragSrc = '#version 300 es\n' +
    'precision highp float;\n' +
    'out vec4 O;\n' +
    'uniform vec2 resolution;\n' +
    'uniform float time;\n' +
    '#define FC gl_FragCoord.xy\n' +
    '#define T time\n' +
    '#define R resolution\n' +
    '#define MN min(R.x,R.y)\n' +
    // белый шум
    'float rnd(vec2 p){p=fract(p*vec2(12.9898,78.233));p+=dot(p,p+34.56);return fract(p.x*p.y);}\n' +
    // value-шум
    'float noise(in vec2 p){vec2 i=floor(p),f=fract(p),u=f*f*(3.-2.*f);' +
    'float a=rnd(i),b=rnd(i+vec2(1,0)),c=rnd(i+vec2(0,1)),d=rnd(i+1.);' +
    'return mix(mix(a,b,u.x),mix(c,d,u.x),u.y);}\n' +
    // фрактальный шум
    'float fbm(vec2 p){float t=.0,a=1.;mat2 m=mat2(1.,-.5,.2,1.2);' +
    'for(int i=0;i<6;i++){t+=a*noise(p);p*=2.*m;a*=.5;}return t;}\n' +
    // клубы дыма
    'float clouds(vec2 p){float d=1.,t=.0;' +
    'for(float i=.0;i<3.;i++){float a=d*fbm(i*10.+p.x*.2+.2*(1.+i)*p.y+d+i*i+p);' +
    't=mix(t,d,a);d=a;p*=2./(i+1.);}return t;}\n' +
    'void main(){\n' +
    '  vec2 uv=(FC-.5*R)/MN, st=uv*vec2(1.6,1.);\n' +
    // два слоя дыма, плывущие в разные стороны
    '  float c1=clouds(vec2(st.x+T*.12, -st.y+T*.03));\n' +
    '  float c2=clouds(vec2(st.x*1.4-T*.07+5., -st.y*1.4-T*.04+9.));\n' +
    // палитра сайта: светлый фон + фиолет/виолет
    '  vec3 base=vec3(.965,.965,.972);\n' +   // #f6f6f8
    '  vec3 p1=vec3(.357,.239,.961);\n' +     // #5b3df5
    '  vec3 p2=vec3(.659,.333,.969);\n' +     // #a855f7
    '  float m1=smoothstep(.15,1.25,c1);\n' +
    '  float m2=smoothstep(.25,1.35,c2);\n' +
    '  vec3 col=base;\n' +
    '  col=mix(col,p2,m2*.30);\n' +
    '  col=mix(col,p1,m1*.42);\n' +
    '  O=vec4(col,1.);\n' +
    '}';

  function compile(type, src) {
    var s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      console.error('shader-bg:', gl.getShaderInfoLog(s));
    }
    return s;
  }

  var prog = gl.createProgram();
  gl.attachShader(prog, compile(gl.VERTEX_SHADER, vertSrc));
  gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, fragSrc));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
    console.error('shader-bg:', gl.getProgramInfoLog(prog));
    return;
  }
  gl.useProgram(prog);

  var buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, 1, -1, -1, 1, 1, 1, -1]), gl.STATIC_DRAW);
  var loc = gl.getAttribLocation(prog, 'position');
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

  var uRes = gl.getUniformLocation(prog, 'resolution');
  var uTime = gl.getUniformLocation(prog, 'time');

  // рендерим в половинном разрешении — дёшево, дым всё равно мягкий
  var dpr = Math.max(1, 0.5 * (window.devicePixelRatio || 1));
  function resize() {
    canvas.width = Math.floor(window.innerWidth * dpr);
    canvas.height = Math.floor(window.innerHeight * dpr);
    gl.viewport(0, 0, canvas.width, canvas.height);
  }
  resize();
  window.addEventListener('resize', resize);

  function draw(t) {
    gl.uniform2f(uRes, canvas.width, canvas.height);
    gl.uniform1f(uTime, t * 1e-3);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) {
    draw(0); // уважаем «уменьшить движение» — рисуем один статичный кадр
  } else {
    (function loop(now) {
      draw(now);
      requestAnimationFrame(loop);
    })(0);
  }
})();
