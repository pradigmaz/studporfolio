// Самодостаточная реализация popover без зависимостей
document.addEventListener('DOMContentLoaded', function() {
  // Находим все элементы с атрибутом data-bs-toggle="popover"
  const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
  
  // Инициализируем поповеры
  if (popoverTriggerList.length > 0) {
    popoverTriggerList.forEach(function(popoverTriggerEl) {
      // Получаем данные из атрибутов
      const title = popoverTriggerEl.getAttribute('data-bs-title') || '';
      const content = popoverTriggerEl.getAttribute('data-bs-content') || '';
      const placement = popoverTriggerEl.getAttribute('data-bs-placement') || 'top';
      
      // Создаем элемент popover
      const createPopoverElement = function() {
        const popoverEl = document.createElement('div');
        popoverEl.className = 'popover';
        popoverEl.setAttribute('role', 'tooltip');
        
        // Стили для попоера
        popoverEl.style.position = 'absolute';
        popoverEl.style.zIndex = '1070';
        popoverEl.style.maxWidth = '276px';
        popoverEl.style.padding = '0';
        popoverEl.style.border = '1px solid rgba(0,0,0,.2)';
        popoverEl.style.borderRadius = '.3rem';
        popoverEl.style.backgroundColor = '#fff';
        popoverEl.style.boxShadow = '0 .25rem .5rem rgba(0,0,0,.2)';
        
        // Создаем HTML структуру popover
        popoverEl.innerHTML = `
          <div class="popover-arrow"></div>
          <h3 class="popover-header">${title}</h3>
          <div class="popover-body">${content}</div>
        `;
        
        return popoverEl;
      };
      
      // Функция размещения поповера
      const positionPopover = function(popoverEl, triggerEl, placement) {
        const triggerRect = triggerEl.getBoundingClientRect();
        
        // Добавляем popover в body для правильного расчета размеров
        document.body.appendChild(popoverEl);
        
        // Получаем размеры popover
        const popoverRect = popoverEl.getBoundingClientRect();
        
        // Вычисляем позицию в зависимости от размещения
        let top, left;
        
        switch(placement) {
          case 'top':
            top = triggerRect.top - popoverRect.height - 10;
            left = triggerRect.left + (triggerRect.width - popoverRect.width) / 2;
            break;
          case 'bottom':
            top = triggerRect.bottom + 10;
            left = triggerRect.left + (triggerRect.width - popoverRect.width) / 2;
            break;
          case 'left':
            top = triggerRect.top + (triggerRect.height - popoverRect.height) / 2;
            left = triggerRect.left - popoverRect.width - 10;
            break;
          case 'right':
            top = triggerRect.top + (triggerRect.height - popoverRect.height) / 2;
            left = triggerRect.right + 10;
            break;
        }
        
        // Корректируем позицию с учетом прокрутки
        top += window.scrollY;
        left += window.scrollX;
        
        // Устанавливаем позицию
        popoverEl.style.top = `${top}px`;
        popoverEl.style.left = `${left}px`;
      };
      
      // Обработчик клика для показа/скрытия popover
      let popoverEl = null;
      let isVisible = false;
      
      popoverTriggerEl.addEventListener('click', function(event) {
        event.preventDefault();
        
        if (isVisible && popoverEl) {
          // Если уже отображается, скрываем
          document.body.removeChild(popoverEl);
          popoverEl = null;
          isVisible = false;
        } else {
          // Создаем и отображаем
          popoverEl = createPopoverElement();
          positionPopover(popoverEl, popoverTriggerEl, placement);
          isVisible = true;
          
          // Добавляем обработчик клика вне popover для скрытия
          setTimeout(function() {
            document.addEventListener('click', function closePopover(e) {
              if (popoverEl && !popoverEl.contains(e.target) && e.target !== popoverTriggerEl) {
                if (popoverEl.parentNode) {
                  document.body.removeChild(popoverEl);
                }
                popoverEl = null;
                isVisible = false;
                document.removeEventListener('click', closePopover);
              }
            });
          }, 0);
        }
      });
    });
  }
}); 