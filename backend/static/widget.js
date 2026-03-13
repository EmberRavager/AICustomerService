(function () {
  function initWidget() {
    var script = document.currentScript;
    var tenantKey = script.getAttribute('data-tenant-key') || '';
    var title = script.getAttribute('data-title') || '在线客服';
    var url = script.getAttribute('data-url') || 'http://localhost:3000/widget';

    var container = document.createElement('div');
    container.id = 'aics-widget-container';
    container.style.position = 'fixed';
    container.style.bottom = '20px';
    container.style.right = '20px';
    container.style.zIndex = '999999';

    var button = document.createElement('button');
    button.innerText = title;
    button.style.background = '#1677ff';
    button.style.color = '#fff';
    button.style.border = 'none';
    button.style.borderRadius = '20px';
    button.style.padding = '10px 16px';
    button.style.cursor = 'pointer';
    button.style.boxShadow = '0 6px 16px rgba(0,0,0,0.12)';

    var iframe = document.createElement('iframe');
    iframe.style.width = '360px';
    iframe.style.height = '520px';
    iframe.style.border = 'none';
    iframe.style.borderRadius = '12px';
    iframe.style.boxShadow = '0 12px 24px rgba(0,0,0,0.2)';
    iframe.style.display = 'none';
    iframe.style.marginTop = '10px';
    iframe.src = url + (tenantKey ? ('?tenant_key=' + encodeURIComponent(tenantKey)) : '');

    button.onclick = function () {
      iframe.style.display = iframe.style.display === 'none' ? 'block' : 'none';
    };

    container.appendChild(button);
    container.appendChild(iframe);
    document.body.appendChild(container);
  }

  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    initWidget();
  } else {
    document.addEventListener('DOMContentLoaded', initWidget);
  }
})();
