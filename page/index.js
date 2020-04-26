// Customize these...
var n = 25,
    duration = 1.25;

// ...not these
var c = document.getElementById("c"),
    ctx = c.getContext("2d"),
    cw = (c.width = window.innerWidth),
    ch = (c.height = window.innerHeight),
    img = new Image(),
    particles = [],
    particleNumber = 0,
    Particle = function(_i) {
      this.index = _i;
      this.draw = function() {
        ctx.globalAlpha = this.alpha;
        ctx.globalCompositeOperation = 'lighter';
        // if (particleNumber%5==0) ctx.drawImage(img, this.x, this.y, this.size, this.size*1.1);
        if (particleNumber%this.index==0) ctx.drawImage(img, this.x, this.y-2, this.size, this.size*1.3);
        ctx.drawImage(img, this.x, this.y, this.size, this.size);
      }
    };


function setParticle(p) {
  particleNumber++;
  var _size = rand(4, 12), // px width + height
      _dur = rand(duration, duration+(_size/10)),
      _tl = new TimelineMax()
            .fromTo(p, _dur, { x:rand(-_size, cw),
                               y:ch,
                               size:_size
                              },{
                               x:'+='+rand(_size*-10,_size*45),
                               y:-_size,
                               size:15,                               
                               ease:Sine.easeIn,
                               onComplete:function(){ setParticle(p); }
                              }, 0)
            //.fromTo(p,  _dur/3, {alpha:0.3}, {alpha:1, ease:Power1.easeInOut}, 0)
            .to(p,      _dur/4, {size:1}, _dur-_dur/4)
  if (particleNumber<n) _tl.seek(_dur*rand()); //fast forward on first run
}


// First run
for (var i=0; i<n; i++) {
    particles.push(new Particle(i));
    setParticle(particles[i]);      
}

TweenMax.ticker.addEventListener("tick", function(){
  ctx.clearRect(0, 0, cw, ch);
  for (var i=0; i<n; i++) particles[i].draw();
});

  
window.addEventListener('resize', function() {
  particleNumber = 0;  
  cw = (c.width = window.innerWidth);
  ch = (c.height = window.innerHeight);
  for (var i=0; i<n; i++) {
    TweenMax.killTweensOf(particles[i]);
    setParticle(particles[i]);
  }
});


function rand(min=0, max=1) {
  return min + (max-min)*Math.random();
}


img.src = "data:image/png;base64,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";