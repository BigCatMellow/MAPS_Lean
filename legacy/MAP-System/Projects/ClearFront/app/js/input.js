(() => {
  'use strict';
  const CF = (window.CF = window.CF || {});

  // Card-preview gesture layer (DEC-CF-007). This installer deliberately has
  // no ctx dependency: the behavior is a self-contained DOM-event closure.
  CF.installInputModule = () => {
    const canPeek = window.matchMedia('(min-width: 761px) and (hover: hover)');
    let peekEl = null, peekSrc = null;
    function removePeek() {
      if (peekEl) { peekEl.remove(); peekEl = null; peekSrc = null; }
    }
    document.addEventListener('mouseover', (e) => {
      if (!canPeek.matches) return;
      const card = e.target.closest('.card');
      if (!card || card.classList.contains('card-peek') || card.closest('.card-catalog, .deck-select-modal')) { if (!e.target.closest('.card-peek')) removePeek(); return; }
      if (card === peekSrc) return;
      removePeek();
      peekSrc = card;
      peekEl = card.cloneNode(true);
      peekEl.classList.add('card-peek');
      peekEl.classList.remove('clickable', 'selected', 'targetable');
      document.body.appendChild(peekEl);
      const r = card.getBoundingClientRect();
      const pw = 250, ph = peekEl.offsetHeight || 220;
      let x = r.right + 12;
      if (x + pw > window.innerWidth - 8) x = r.left - pw - 12;
      if (x < 8) x = Math.min(window.innerWidth - pw - 8, Math.max(8, r.left));
      let y = Math.min(Math.max(8, r.top - 20), window.innerHeight - ph - 8);
      peekEl.style.left = x + 'px';
      peekEl.style.top = y + 'px';
      requestAnimationFrame(() => peekEl && peekEl.classList.add('show'));
    });
    document.addEventListener('mouseout', (e) => {
      if (peekSrc && !peekSrc.contains(e.relatedTarget)) removePeek();
    });
    document.addEventListener('click', removePeek, true);
    window.addEventListener('scroll', removePeek, true);

    // Touch: press-and-hold any card to inspect it full-size
    let holdTimer = null, holdShown = false, backdrop = null;
    function removeTouchPeek() {
      clearTimeout(holdTimer); holdTimer = null;
      if (backdrop) { backdrop.remove(); backdrop = null; }
      removePeek();
    }
    document.addEventListener('touchstart', (e) => {
      const card = e.target.closest('.card');
      if (!card || card.classList.contains('card-peek')) return;
      holdShown = false;
      clearTimeout(holdTimer);
      holdTimer = setTimeout(() => {
        holdShown = true;
        removePeek();
        backdrop = document.createElement('div');
        backdrop.className = 'peek-backdrop';
        document.body.appendChild(backdrop);
        peekSrc = card;
        peekEl = card.cloneNode(true);
        peekEl.classList.add('card-peek', 'touch');
        peekEl.classList.remove('clickable', 'selected', 'targetable');
        document.body.appendChild(peekEl);
        requestAnimationFrame(() => peekEl && peekEl.classList.add('show'));
        if (navigator.vibrate) navigator.vibrate(10);
      }, 350);
    }, { passive: true });
    document.addEventListener('touchmove', () => { if (!holdShown) { clearTimeout(holdTimer); holdTimer = null; } }, { passive: true });
    document.addEventListener('touchend', (e) => {
      if (holdShown) { e.preventDefault(); removeTouchPeek(); holdShown = false; }
      else { clearTimeout(holdTimer); holdTimer = null; }
    }, { passive: false });
    document.addEventListener('touchcancel', () => { removeTouchPeek(); holdShown = false; }, { passive: true });
    // Swallow the click that follows a completed hold so the card isn't played
    document.addEventListener('click', (e) => {
      if (holdShown) { e.stopPropagation(); e.preventDefault(); holdShown = false; }
    }, true);
  };
})();
