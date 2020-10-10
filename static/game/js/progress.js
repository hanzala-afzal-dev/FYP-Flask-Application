
// Test code

$('.progress').each((_, progress) => {
  
    const steps = $('> div.right > div', progress);
  
    steps.each((i, el) => $(el).mouseenter(e => onHover(el)));
  
    const onHover = (el) => {
        steps.removeClass(['prev','current']);
        el.classList.add('current');
        $(el).prevAll().slice(1).addClass('prev');
      };
  })
  