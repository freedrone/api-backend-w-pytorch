let src_img;
let src_ext;

let mask;

const stroke_width = 5; // in pixels

let setBackground = (image) => {
  let canvas = document.getElementById('paint');
  let ctx = canvas.getContext('2d');

  let background = new Image();
  background.src = image;
  background.onload = () => {
    ctx.drawImage(background, 0, 0, background.naturalWidth, background.naturalHeight, 0, 0, 256, 256);
  };
}

let onFileUpload = (event) => {
  let files;
  if (event.type) {
    event.preventDefault();
    if (event.dataTransfer) {
      files = event.dataTransfer.files;
    } else if (event.target) {
      files = event.target.files;
    }
  } else {
    files = event;
  }

  const reader = new window.FileReader();
  if (files[0]) {
    reader.readAsDataURL(files[0]);
  }
  reader.onload = async () => {
    if (!/\.(gif|jpg|jpeg|tiff|png)$/i.test(files[0].name)) {
      return;
    }

    src_img = reader.result;
    src_ext = files[0].name.split('.').pop();

    console.log(src_ext);
    console.log(src_img);

    setBackground(src_img);
  };
};
document.getElementById('img-input').onchange = onFileUpload;

let reset = () => { setBackground(src_img); }
document.getElementById('rset-btn').onclick = reset;

let save = () => {
  let canvas = document.getElementById('paint');
  let img = canvas.toDataURL();

  let mask_img = mask.toDataURL();

  axios({
    method: 'post',
    url: '/upload',
    data: {
      'image': img,
      'mask' : mask_img,
      'ext'  : src_ext,
    },
    config: {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }
  });
}
document.getElementById('pred-btn').onclick = () => save();

(function() {
  let canvas = document.querySelector('#paint');
  let ctx = canvas.getContext('2d');

  let sketch = document.querySelector('#sketch');
  let sketch_style = getComputedStyle(sketch);
  canvas.width = parseInt(sketch_style.getPropertyValue('width'));
  canvas.height = parseInt(sketch_style.getPropertyValue('height'));

  let offsetLeft = sketch.getBoundingClientRect().left;
  let offsetTop = sketch.getBoundingClientRect().top;

  let mouse = {x: 0, y: 0};
  let last_mouse = {x: 0, y: 0};

  /* Mouse Capturing Work */
  canvas.addEventListener('mousemove', function(e) {
    last_mouse.x = mouse.x;
    last_mouse.y = mouse.y;

    mouse.x = e.pageX - offsetLeft;
    mouse.y = e.pageY - offsetTop;
  }, false);

  /* Drawing on Paint App */
  ctx.lineWidth = stroke_width;
  ctx.lineJoin = 'round';
  ctx.lineCap = 'round';
  ctx.strokeStyle = "#7f7f7f";

  mask = document.createElement('canvas');
  let mask_ctx = mask.getContext('2d');
  mask_ctx.canvas.width = 256;
  mask_ctx.canvas.height = 256;
  mask_ctx.fillStyle = 'black';
  mask_ctx.fillRect(0, 0, 256, 256);
  mask_ctx.lineWidth = stroke_width;
  mask_ctx.strokeStyle = 'white';

  canvas.addEventListener('mousedown', function(e) {
    canvas.addEventListener('mousemove', onPaint, false);
  }, false);

  canvas.addEventListener('mouseup', function() {
    canvas.removeEventListener('mousemove', onPaint, false);
  }, false);

  canvas.addEventListener('mouseout', function () {
    canvas.removeEventListener('mousemove', onPaint, false);
  }, false);

  let onPaint = function() {
    ctx.beginPath();
    ctx.moveTo(last_mouse.x, last_mouse.y);
    ctx.lineTo(mouse.x, mouse.y);
    ctx.closePath();

    mask_ctx.beginPath();
    mask_ctx.moveTo(last_mouse.x, last_mouse.y);
    mask_ctx.lineTo(mouse.x, mouse.y);
    mask_ctx.closePath();

    ctx.stroke();
    mask_ctx.stroke();
  };
}());
