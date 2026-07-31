/**
 * 学生成绩管理系统
 */

$(document).ready(function() {
    // 移动端侧边栏
    $('[data-sidebar-toggle]').on('click', function() {
        $('#sidebar').toggleClass('open');
        $('.sidebar-backdrop').toggleClass('show');
    });

    // 学号：仅数字，最多 8 位
    $('input[name="student_id"]').on('input', function() {
        this.value = this.value.replace(/\D/g, '').slice(0, 8);
    });

    // 分数：限制 0–100
    $('input[name="score"]').on('input', function() {
        var val = parseInt(this.value, 10);
        if (this.value !== '') {
            if (val > 100) this.value = 100;
            if (val < 0) this.value = 0;
        }
    });

    // 快捷键：Alt+1~5 切换页面
    $(document).on('keydown', function(e) {
        if (!e.altKey) return;
        var navMap = { '1': '/', '2': '/grades', '3': '/analysis', '4': '/charts', '5': '/clean' };
        if (navMap[e.key]) {
            e.preventDefault();
            window.location.href = navMap[e.key];
        }
    });
});

function formatScore(score) {
    if (!score || score === 'nan' || score === '') {
        return '<span class="score-tag empty">—</span>';
    }
    var val = parseInt(score, 10);
    var cls = val >= 90 ? 'high' : val >= 60 ? 'mid' : 'low';
    return '<span class="score-tag ' + cls + '">' + score + '</span>';
}

function showToast(message, type) {
    type = type || 'info';
    var clsMap = { success: 'flash-success', error: 'flash-danger', info: 'flash-info', warning: 'flash-warning' };
    var $el = $('<div class="flash ' + (clsMap[type] || 'flash-info') + '">' + message + '</div>');
    $('.flash-stack').length
        ? $('.flash-stack').append($el)
        : $('.topbar').after('<div class="flash-stack"></div>').next().append($el);
    setTimeout(function() { $el.fadeOut(200, function() { $(this).remove(); }); }, 3500);
}

function debounce(func, wait) {
    var timeout;
    return function() {
        var ctx = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(function() { func.apply(ctx, args); }, wait);
    };
}
