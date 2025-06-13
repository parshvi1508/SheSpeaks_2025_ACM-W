// Petal animation for SheSpeaks 2025

class Petal {
  constructor() {
    this.x = Math.random() * window.innerWidth;
    this.y = Math.random() * -100;
    this.size = Math.random() * 15 + 5;
    this.speed = Math.random() * 1 + 0.5;
    this.rotation = Math.random() * 360;
    this.rotationSpeed = (Math.random() - 0.5) * 2;
    this.swingAmount = Math.random() * 3;
    this.swingSpeed = Math.random() * 0.02;
    this.swingOffset = Math.random() * Math.PI * 2;
    this.opacity = Math.random() * 0.6 + 0.4;
    this.hue = Math.random() * 30 + 330; // Pink hues
  }

  update() {
    this.y += this.speed;
    this.x += Math.sin(this.y * this.swingSpeed + this.swingOffset) * this.swingAmount;
    this.rotation += this.rotationSpeed;

    // Reset when off screen
    if (this.y > window.innerHeight + 100) {
      this.y = Math.random() * -100;
      this.x = Math.random() * window.innerWidth;
    }
  }

  draw(ctx) {
    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.rotate((this.rotation * Math.PI) / 180);
    ctx.globalAlpha = this.opacity;
    
    // Create petal shape
    ctx.beginPath();
    ctx.fillStyle = `hsla(${this.hue}, 100%, 80%, ${this.opacity})`;
    ctx.ellipse(0, 0, this.size, this.size / 2, 0, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.restore();
  }
}

class PetalAnimation {
  constructor() {
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
    this.canvas.id = 'bg-canvas';
    document.body.insertBefore(this.canvas, document.body.firstChild);
    
    this.petals = [];
    this.init();
    
    window.addEventListener('resize', () => this.resize());
    this.animate();
  }
  
  init() {
    this.resize();
    
    // Create petals
    const numPetals = Math.floor(window.innerWidth / 15); // Adjust density
    for (let i = 0; i < numPetals; i++) {
      this.petals.push(new Petal());
    }
  }
  
  resize() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }
  
  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    this.petals.forEach(petal => {
      petal.update();
      petal.draw(this.ctx);
    });
    
    requestAnimationFrame(() => this.animate());
  }
}

// Start animation when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new PetalAnimation();
});