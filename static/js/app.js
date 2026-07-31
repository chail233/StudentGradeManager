/**
 * 学生成绩管理与分析系统 - 主脚本
 */

$(document).ready(function() {
    // ===== 自动隐藏消息提示 =====
    setTimeout(function() {
        $('.alert-dismissible').alert('close');
    }, 5000);

    // ===== 表单输入自动格式化 =====
    // 学号输入框：只允许数字
    $('input[name="student_id"]').on('input', function() {
        this.value = this.value.replace(/\D/g, '').slice(0, 8);
    });

    // 分数输入框：限制 0-100
    $('input[name="score"]').on('input', function() {
        var val = parseInt(this.value);
        if (this.value !== '') {
            if (val > 100) this.value = 100;
            if (val < 0) this.value = 0;
        }
    });

    // ===== 表格行点击高亮 =====
    $('.table tbody tr').on('click', function() {
        $(this).toggleClass('table-active');
    });

    // ===== 键盘快捷键导航 =====
    $(document).on('keydown', function(e) {
        // Alt+数字 快速导航
        if (e.altKey) {
            var navMap = {
                '1': '/',
                '2': '/grades',
                '3': '/analysis',
                '4': '/charts',
                '5': '/clean'
            };
            var path = navMap[e.key];
            if (path) {
                e.preventDefault();
                window.location.href = path;
            }
        }
    });

    // ===== 页面加载完成后的动画 =====
    $('.card').each(function(index) {
        var $card = $(this);
        setTimeout(function() {
            $card.css('opacity', '1');
        }, index * 50);
    });
});

// ===== 工具函数 =====

/**
 * 格式化分数显示
 * @param {string|number} score - 分数值
 * @returns {string} 格式化后的 HTML 字符串
 */
function formatScore(score) {
    if (!score || score === 'nan' || score === '') {
        return '<span class="text-muted">-</span>';
    }
    var val = parseInt(score);
    var cls = val >= 90 ? 'bg-success' : val >= 60 ? 'bg-info' : 'bg-danger';
    return '<span class="badge ' + cls + '">' + score + '</span>';
}

/**
 * 显示 Toast 消息
 * @param {string} message - 消息内容
 * @param {string} type - 类型：success/error/info/warning
 */
function showToast(message, type) {
    type = type || 'info';
    var bgMap = {
        'success': 'bg-success',
        'error': 'bg-danger',
        'info': 'bg-info',
        'warning': 'bg-warning text-dark'
    };
    var toastHtml = '<div class="position-fixed bottom-0 end-0 p-3" style="z-index: 9999">' +
        '<div class="toast align-items-center text-white ' + (bgMap[type] || 'bg-info') + ' border-0" role="alert">' +
        '<div class="d-flex">' +
        '<div class="toast-body">' + message + '</div>' +
        '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>' +
        '</div></div></div>';

    var $toastContainer = $(toastHtml).appendTo('body');
    var toast = new bootstrap.Toast($toastContainer.find('.toast')[0]);
    toast.show();

    setTimeout(function() {
        $toastContainer.remove();
    }, 3000);
}

/**
 * 防抖函数
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
function debounce(func, wait) {
    var timeout;
    return function() {
        var context = this;
        var args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(function() {
            func.apply(context, args);
        }, wait);
    };
}