$(document).ready(function() {
    // 탭 기능 활성화
    $('.nav-tabs a').click(function(e) {
      e.preventDefault();
      $(this).tab('show');
    });
  });