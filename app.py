import os
import re
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # 非交互式后端，防止 plt.show() 阻塞
import matplotlib.pyplot as plt
import pandas as pd

# 设置 Matplotlib 中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from StudentData.DataProcesser import StuData

app = Flask(__name__)
app.secret_key = 'student_grade_manager_secret_key'

# 数据文件路径
DATA_PATH = 'data/scores.csv'
SUBJECTS = ['语文', '数学', '英语']
PATTERN_ID = r'^\d{8}$'
PATTERN_SCORE = r'^(\d{1,2}|100)$'


def get_stu_data():
    """获取 StuData 实例，确保文件存在且格式正确"""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    if not os.path.exists(DATA_PATH) or os.path.getsize(DATA_PATH) == 0:
        # 写入一个带表头的空占位文件（StuData 需要至少一行数据才能正常初始化）
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            f.write('placeholder,placeholder,0,0,0\n')
    return StuData(DATA_PATH)


def df_to_list(df):
    """将 DataFrame 转换为前端可用的列表（过滤掉占位行）"""
    records = []
    for idx, row in df.iterrows():
        if str(idx) == 'placeholder':
            continue
        records.append({
            'id': idx,
            'name': row.get('name', ''),
            '语文': row.get('语文', ''),
            '数学': row.get('数学', ''),
            '英语': row.get('英语', '')
        })
    return records


def get_stats():
    """从 StuData 获取统计数据"""
    try:
        stu = get_stu_data()
        df = stu.get_df()
        if df.empty:
            return None

        # 各科成绩转为数值
        score_df = df[SUBJECTS].apply(pd.to_numeric, errors='coerce')

        total = len(df)
        person_total = score_df.sum(axis=1)

        # 各科平均分
        subject_avgs = {}
        for s in SUBJECTS:
            subject_avgs[s] = round(score_df[s].mean(), 2) if not score_df[s].isna().all() else 0

        # 各科及格率/优秀率
        subject_pass = {}
        subject_excellent = {}
        for s in SUBJECTS:
            valid = score_df[s].dropna()
            n = len(valid)
            subject_pass[s] = round((valid >= 60).sum() / n * 100, 2) if n > 0 else 0
            subject_excellent[s] = round((valid >= 90).sum() / n * 100, 2) if n > 0 else 0

        pass_count = sum(1 for _, r in score_df.iterrows() if all(r >= 60))
        excellent_count = sum(1 for _, r in score_df.iterrows() if all(r >= 90))

        return {
            'total_students': total,
            'total_scores': int(score_df.sum().sum()),
            'avg_score': round(person_total.mean(), 2),
            'max_score': int(person_total.max()),
            'min_score': int(person_total.min()),
            'pass_rate': round(pass_count / total * 100, 2),
            'excellent_rate': round(excellent_count / total * 100, 2),
            'subject_avgs': subject_avgs,
            'subject_pass': subject_pass,
            'subject_excellent': subject_excellent
        }
    except Exception:
        return None

# ==================== 模板上下文处理器 ====================

@app.context_processor
def inject_current_year():
    """注入当前年份到所有模板"""
    return {'current_year': datetime.now().year}


# ==================== 路由 ====================

@app.route('/')
def dashboard():
    """首页仪表盘"""
    stats = get_stats()
    return render_template('dashboard.html', stats=stats, active_page='dashboard')


@app.route('/grades')
def grades():
    """成绩管理页面"""
    try:
        stu = get_stu_data()
        students = df_to_list(stu.get_df())
        return render_template('grades.html', students=students, subjects=SUBJECTS, active_page='grades')
    except Exception as e:
        return render_template('grades.html', students=[], subjects=SUBJECTS, active_page='grades', error=str(e))


@app.route('/grades/add', methods=['POST'])
def add_grade():
    """添加学生成绩"""
    sid = request.form.get('student_id', '').strip()
    name = request.form.get('student_name', '').strip()
    subject = request.form.get('subject', '')
    score = request.form.get('score', '').strip()

    errors = []
    if not re.fullmatch(PATTERN_ID, sid):
        errors.append('学号格式错误（需为8位数字）')
    if not name:
        errors.append('姓名不能为空')
    if subject not in SUBJECTS:
        errors.append('科目无效')
    if not re.fullmatch(PATTERN_SCORE, score):
        errors.append('分数格式错误（需为0-100的整数）')

    if errors:
        return jsonify({'success': False, 'errors': errors})

    try:
        stu = get_stu_data()
        df = stu.get_df()

        if sid in df.index:
            if pd.notna(df.loc[sid, subject]):
                return jsonify({'success': False, 'errors': [f'{sid} 的 {subject} 成绩已存在，请使用修改功能']})
            df.loc[sid, subject] = score
            df.loc[sid, 'name'] = name
        else:
            new_row = {'name': name, '语文': pd.NA, '数学': pd.NA, '英语': pd.NA}
            new_row[subject] = score
            df.loc[sid] = [new_row['name'], new_row['语文'], new_row['数学'], new_row['英语']]

        stu.save_df()
        return jsonify({'success': True, 'message': f'学生 {name}({sid}) 的 {subject} 成绩 {score} 分添加成功！'})
    except Exception as e:
        return jsonify({'success': False, 'errors': [f'添加失败：{str(e)}']})


@app.route('/grades/modify', methods=['POST'])
def modify_grade():
    """修改学生成绩"""
    sid = request.form.get('student_id', '').strip()
    subject = request.form.get('subject', '')
    score = request.form.get('score', '').strip()

    errors = []
    if not re.fullmatch(PATTERN_ID, sid):
        errors.append('学号格式错误（需为8位数字）')
    if subject not in SUBJECTS:
        errors.append('科目无效')
    if not re.fullmatch(PATTERN_SCORE, score):
        errors.append('分数格式错误（需为0-100的整数）')

    if errors:
        return jsonify({'success': False, 'errors': errors})

    try:
        stu = get_stu_data()
        df = stu.get_df()
        if sid not in df.index:
            return jsonify({'success': False, 'errors': ['该学号不存在']})
        df.loc[sid, subject] = score
        stu.save_df()
        return jsonify({'success': True, 'message': f'{sid} 的 {subject} 成绩已修改为 {score} 分'})
    except Exception as e:
        return jsonify({'success': False, 'errors': [f'修改失败：{str(e)}']})


@app.route('/grades/delete', methods=['POST'])
def delete_grade():
    """删除学生成绩"""
    sid = request.form.get('student_id', '').strip()
    subject = request.form.get('subject', '')
    delete_all = request.form.get('delete_all', 'false') == 'true'

    if not re.fullmatch(PATTERN_ID, sid):
        return jsonify({'success': False, 'errors': ['学号格式错误（需为8位数字）']})

    try:
        stu = get_stu_data()
        df = stu.get_df()
        if sid not in df.index:
            return jsonify({'success': False, 'errors': ['该学号不存在']})

        if delete_all or subject == 'all':
            df.loc[sid, '语文'] = pd.NA
            df.loc[sid, '数学'] = pd.NA
            df.loc[sid, '英语'] = pd.NA
            msg = f'{sid} 所有成绩已删除'
        else:
            if subject not in SUBJECTS:
                return jsonify({'success': False, 'errors': ['科目无效']})
            df.loc[sid, subject] = pd.NA
            msg = f'{sid} 的 {subject} 成绩已删除'

        stu.save_df()
        return jsonify({'success': True, 'message': msg})
    except Exception as e:
        return jsonify({'success': False, 'errors': [f'删除失败：{str(e)}']})


@app.route('/grades/query', methods=['POST'])
def query_grade():
    """查询学生成绩"""
    sid = request.form.get('student_id', '').strip()

    if not re.fullmatch(PATTERN_ID, sid):
        return jsonify({'success': False, 'errors': ['学号格式错误（需为8位数字）']})

    try:
        stu = get_stu_data()
        df = stu.get_df()
        if sid not in df.index:
            return jsonify({'success': False, 'errors': ['该学号不存在']})

        row = df.loc[sid]
        return jsonify({
            'success': True,
            'student': {
                'id': sid,
                'name': row.get('name', ''),
                '语文': str(row.get('语文', '')),
                '数学': str(row.get('数学', '')),
                '英语': str(row.get('英语', ''))
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'errors': [f'查询失败：{str(e)}']})


@app.route('/analysis')
def analysis():
    """统计分析页面"""
    try:
        stu = get_stu_data()
        df = stu.get_df()
        if df.empty:
            return render_template('analysis.html', active_page='analysis', has_data=False)

        score_df = df[SUBJECTS].apply(pd.to_numeric, errors='coerce')

        # 全班统计
        total_students = len(df)
        class_total = int(score_df.sum().sum())
        class_avg = round(score_df.sum(axis=1).mean(), 2)
        class_max = int(score_df.sum(axis=1).max())
        class_min = int(score_df.sum(axis=1).min())

        # 各科统计
        subject_stats = []
        for s in SUBJECTS:
            valid = score_df[s].dropna()
            if len(valid) > 0:
                subject_stats.append({
                    'name': s,
                    'avg': round(valid.mean(), 2),
                    'max': int(valid.max()),
                    'min': int(valid.min()),
                    'pass_rate': round((valid >= 60).sum() / len(valid) * 100, 2),
                    'excellent_rate': round((valid >= 90).sum() / len(valid) * 100, 2)
                })

        # 个人排名（按总分）
        person_df = df.copy()
        person_df['总分'] = score_df.sum(axis=1)
        person_df['平均分'] = round(score_df.mean(axis=1), 2)
        person_df = person_df.sort_values('总分', ascending=False)
        rankings = []
        for rank, (idx, row) in enumerate(person_df.iterrows(), 1):
            rankings.append({
                'rank': rank,
                'id': idx,
                'name': row.get('name', ''),
                '语文': row.get('语文', ''),
                '数学': row.get('数学', ''),
                '英语': row.get('英语', ''),
                'total': int(row['总分']),
                'avg': row['平均分']
            })

        # 不及格学生
        fail_students = []
        for idx, row in df.iterrows():
            scores = score_df.loc[idx]
            fail_subs = [s for s in SUBJECTS if scores[s] < 60]
            if fail_subs:
                fail_students.append({
                    'id': idx,
                    'name': row.get('name', ''),
                    'fail_subjects': fail_subs
                })

        # 全优学生
        excellent_students = []
        for idx, row in df.iterrows():
            scores = score_df.loc[idx]
            if all(scores[s] >= 90 for s in SUBJECTS):
                excellent_students.append({
                    'id': idx,
                    'name': row.get('name', '')
                })

        return render_template('analysis.html', active_page='analysis', has_data=True,
                               total_students=total_students, class_total=class_total,
                               class_avg=class_avg, class_max=class_max, class_min=class_min,
                               subject_stats=subject_stats, rankings=rankings,
                               fail_students=fail_students, excellent_students=excellent_students)
    except Exception as e:
        return render_template('analysis.html', active_page='analysis', has_data=False, error=str(e))


@app.route('/charts')
def charts():
    """可视化图表页面"""
    try:
        stu = get_stu_data()
        df = stu.get_df()
        if df.empty:
            return render_template('charts.html', active_page='charts', has_data=False)

        # 直接使用 DataFrame 计算，避免调用 StuData 的 plt_average/plt_pie（它们会反复 clean 并调用 plt.show）
        score_df = df[SUBJECTS].apply(pd.to_numeric, errors='coerce')
        if score_df.empty:
            return render_template('charts.html', active_page='charts', has_data=False)

        # 生成 Matplotlib 图表并保存到 static/images/
        img_dir = os.path.join('static', 'images')
        os.makedirs(img_dir, exist_ok=True)

        # 各科平均分柱状图
        plt.figure(figsize=(6, 4))
        subjects_cn = SUBJECTS
        values = [score_df[s].mean() for s in SUBJECTS]
        colors = ['#1d4ed8', '#15803d', '#b45309']
        bars = plt.bar(subjects_cn, values, color=colors, width=0.5, edgecolor='white')
        for bar, v in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                     f'{v:.1f}', ha='center', va='bottom', fontsize=12)
        plt.title('各科平均分', fontsize=14, pad=15)
        plt.ylabel('分数')
        plt.ylim(0, 100)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(img_dir, 'average.png'), dpi=100)
        plt.close()

        # 成绩等级分布饼图
        plt.figure(figsize=(6, 5))
        pie_values = [
            int((score_df < 60).sum().sum()),
            int(((score_df >= 60) & (score_df < 80)).sum().sum()),
            int(((score_df >= 80) & (score_df < 90)).sum().sum()),
            int((score_df >= 90).sum().sum())
        ]
        pie_labels = ['不及格 (<60)', '及格 (60-79)', '良好 (80-89)', '优秀 (90-100)']
        pie_colors = ['#dc2626', '#ca8a04', '#15803d', '#1d4ed8']
        wedges, texts, autotexts = plt.pie(
            pie_values, labels=pie_labels, colors=pie_colors,
            autopct='%1.1f%%', startangle=90, pctdistance=0.85
        )
        for t in autotexts:
            t.set_fontsize(11)
        plt.title('成绩等级分布', fontsize=14, pad=15)
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(os.path.join(img_dir, 'pie.png'), dpi=100)
        plt.close()

        # 准备图表数据供前端 ECharts 使用
        chart_data = {
            'subject_avgs': {
                'categories': SUBJECTS,
                'values': [round(score_df[s].mean(), 2) for s in SUBJECTS]
            },
            'pie_distribution': {
                'labels': pie_labels,
                'values': pie_values
            },
            'student_comparison': {
                'names': [str(row.get('name', '')) for _, row in df.iterrows()],
                '语文': [int(score_df.loc[idx, '语文']) for idx in df.index],
                '数学': [int(score_df.loc[idx, '数学']) for idx in df.index],
                '英语': [int(score_df.loc[idx, '英语']) for idx in df.index]
            }
        }

        return render_template('charts.html', active_page='charts', has_data=True, chart_data=chart_data)
    except Exception as e:
        return render_template('charts.html', active_page='charts', has_data=False, error=str(e))


@app.route('/clean')
def clean_page():
    """数据清洗页面"""
    try:
        stu = get_stu_data()
        df = stu.get_df()
        origin_count = len(df) if not df.empty else 0

        # 检查是否有清洗后的文件
        clean_exists = os.path.exists('data/scores_clean.csv')
        clean_info = None
        if clean_exists:
            clean_df = pd.read_csv('data/scores_clean.csv', header=None,
                                   names=['id', 'name', '语文', '数学', '英语'],
                                   dtype={'id': str})
            clean_info = {
                'count': len(clean_df),
                'records': df_to_list(clean_df)
            }

        return render_template('clean.html', active_page='clean',
                               origin_count=origin_count,
                               clean_exists=clean_exists,
                               clean_info=clean_info)
    except Exception as e:
        return render_template('clean.html', active_page='clean', error=str(e))


@app.route('/clean/run', methods=['POST'])
def run_clean():
    """执行数据清洗"""
    try:
        stu = get_stu_data()
        # 调用 StuData 的 clean 方法
        stu.clean()
        return jsonify({'success': True, 'message': '数据清洗完成！已生成清洗后文件：data/scores_clean.csv'})
    except Exception as e:
        return jsonify({'success': False, 'errors': [f'清洗失败：{str(e)}']})


if __name__ == '__main__':
    app.run(debug=True)