let currentUser = null;
let lastCreatedImage = null;

function showToast(type, title, message, duration = 4000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    toast.innerHTML = `
        <div class="toast-icon">${icons[type]}</div>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(toast);

    if (duration > 0) {
        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}

function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('active');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

async function checkAuth() {
    try {
        const response = await fetch('/api/auth/me');
        const data = await response.json();

        if (data.logged_in) {
            currentUser = data;
            updateAuthUI();
        }
    } catch (e) {
        console.log('检查登录状态失败');
    }
}

function updateAuthUI() {
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const loginTip = document.getElementById('loginTip');
    const createBtn = document.getElementById('createBtn');

    if (currentUser) {
        if (loginBtn) loginBtn.style.display = 'none';
        if (registerBtn) registerBtn.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'inline-flex';
        const displayUid = document.getElementById('displayUid');
        if (displayUid) displayUid.textContent = currentUser.uid;
        if (loginTip) loginTip.style.display = 'none';
        if (createBtn) {
            createBtn.disabled = false;
            createBtn.style.opacity = '1';
        }
    } else {
        if (loginBtn) loginBtn.style.display = 'inline-flex';
        if (registerBtn) registerBtn.style.display = 'inline-flex';
        if (logoutBtn) logoutBtn.style.display = 'none';
        if (loginTip) loginTip.style.display = 'block';
        if (createBtn) {
            createBtn.disabled = true;
            createBtn.style.opacity = '0.5';
        }
    }
}

function openModal(type) {
    const modal = document.getElementById(type + 'Modal');
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(type) {
    const modal = document.getElementById(type + 'Modal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function switchTo(type) {
    closeModal('login');
    closeModal('register');
    setTimeout(() => openModal(type), 100);
}

async function login(e) {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!username || !password) {
        showToast('warning', '输入不完整', '请填写用户名和密码');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });

        const data = await response.json();

        if (data.success) {
            currentUser = data;
            closeModal('login');
            updateAuthUI();
            showToast('success', '登录成功', `欢迎回来，${data.username}！`);
            document.getElementById('loginForm').reset();
        } else {
            showToast('error', '登录失败', data.error || '用户名或密码错误');
        }
    } catch (e) {
        showToast('error', '网络错误', '无法连接到服务器，请重试');
    } finally {
        hideLoading();
    }
}

async function register(e) {
    e.preventDefault();
    const username = document.getElementById('regUsername').value.trim();
    const password = document.getElementById('regPassword').value;

    if (!username || username.length < 3) {
        showToast('warning', '用户名无效', '用户名至少需要3个字符');
        return;
    }

    if (!password || password.length < 6) {
        showToast('warning', '密码无效', '密码至少需要6个字符');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });

        const data = await response.json();

        if (data.success) {
            currentUser = data;
            closeModal('register');
            updateAuthUI();
            showToast('success', '注册成功', `欢迎 ${data.username}，您的用户ID是 ${data.uid}`);
            document.getElementById('registerForm').reset();
        } else {
            showToast('error', '注册失败', data.error || '用户名已存在');
        }
    } catch (e) {
        showToast('error', '网络错误', '无法连接到服务器，请重试');
    } finally {
        hideLoading();
    }
}

async function logout() {
    try {
        await fetch('/api/auth/logout', {method: 'POST'});
        currentUser = null;
        updateAuthUI();
        showToast('info', '已退出', '期待下次再见！');
    } catch (e) {
        showToast('error', '退出失败', '请重试');
    }
}

function showTab(tabId) {
    document.querySelectorAll('.tab').forEach(t => {
        t.classList.remove('active');
        if (t.dataset.tab === tabId) {
            t.classList.add('active');
        }
    });

    document.querySelectorAll('.content').forEach(c => {
        c.classList.remove('active');
    });
    const targetContent = document.getElementById(tabId);
    if (targetContent) {
        targetContent.classList.add('active');
    }

    if (tabId === 'list') {
        loadCharts();
        loadStats();
    }
}

function changeChartType() {
    const type = document.getElementById('chartType').value;
    if (type === 'pie') {
        document.getElementById('xyInputs').style.display = 'none';
        document.getElementById('pieInputs').style.display = 'block';
        document.getElementById('xlabel').required = false;
        document.getElementById('ylabel').required = false;
        document.getElementById('pieLabels').required = true;
        document.getElementById('pieData').required = true;
    } else {
        document.getElementById('xyInputs').style.display = 'block';
        document.getElementById('pieInputs').style.display = 'none';
        document.getElementById('xlabel').required = false;
        document.getElementById('ylabel').required = false;
        document.getElementById('xdata').required = true;
        document.getElementById('ydata').required = true;
        document.getElementById('pieLabels').required = false;
        document.getElementById('pieData').required = false;
    }
}

function validateForm() {
    const chartType = document.getElementById('chartType').value;
    const title = document.getElementById('title').value.trim();

    if (!title || title.length < 2) {
        showToast('warning', '表单验证', '请填写图表标题（至少2个字符）');
        return false;
    }

    if (chartType === 'pie') {
        const labels = document.getElementById('pieLabels').value.trim();
        const data = document.getElementById('pieData').value.trim();

        if (!labels || !data) {
            showToast('warning', '表单验证', '请填写饼图的标签和数据');
            return false;
        }
    } else {
        const xdata = document.getElementById('xdata').value.trim();
        const ydata = document.getElementById('ydata').value.trim();

        if (!xdata || !ydata) {
            showToast('warning', '表单验证', '请填写X轴和Y轴数据');
            return false;
        }
    }

    return true;
}

async function createChart(e) {
    e.preventDefault();

    if (!currentUser) {
        showToast('warning', '需要登录', '请先登录后再创建图表');
        openModal('login');
        return;
    }

    if (!validateForm()) {
        return;
    }

    const title = document.getElementById('title').value.trim();
    const chartType = document.getElementById('chartType').value;
    const createdBy = currentUser.uid;

    let xdata = [], ydata = [], labels = [];

    showLoading();

    try {
        if (chartType === 'pie') {
            labels = document.getElementById('pieLabels').value.split(',').map(s => s.trim());
            ydata = document.getElementById('pieData').value.split(',').map(s => parseFloat(s.trim()));
        } else {
            xdata = document.getElementById('xdata').value.split(',').map(s => s.trim());
            ydata = document.getElementById('ydata').value.split(',').map(s => parseFloat(s.trim()));
        }

        const response = await fetch('/api/charts', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                title,
                chart_type: chartType,
                xdata,
                ydata,
                labels,
                created_by: createdBy,
                xlabel: document.getElementById('xlabel').value,
                ylabel: document.getElementById('ylabel').value
            })
        });

        const result = await response.json();

        if (result.success) {
            lastCreatedImage = result.image;
            document.getElementById('chartImage').src = result.image;
            const resultDiv = document.getElementById('result');
            if (resultDiv) {
                resultDiv.style.display = 'block';
                resultDiv.scrollIntoView({behavior: 'smooth'});
            }
            showToast('success', '创建成功', '图表已保存到数据库');
            loadStats();
        } else {
            showToast('error', '创建失败', result.error || '未知错误');
        }
    } catch (e) {
        showToast('error', '网络错误', '无法创建图表，请重试');
    } finally {
        hideLoading();
    }
}

function downloadChart() {
    if (!lastCreatedImage) {
        showToast('warning', '无可用图表', '请先生成图表');
        return;
    }

    const link = document.createElement('a');
    link.href = lastCreatedImage;
    link.download = `chart_${Date.now()}.png`;
    link.click();

    showToast('success', '下载开始', '图表正在下载');
}

function createAnother() {
    const resultDiv = document.getElementById('result');
    if (resultDiv) {
        resultDiv.style.display = 'none';
    }
    document.getElementById('chartForm').reset();
    window.scrollTo({top: 0, behavior: 'smooth'});
    showToast('info', '准备就绪', '请填写新的图表数据');
}

function resetForm() {
    if (confirm('确定要重置表单吗？所有未保存的数据将丢失。')) {
        document.getElementById('chartForm').reset();
        const resultDiv = document.getElementById('result');
        if (resultDiv) {
            resultDiv.style.display = 'none';
        }
        changeChartType();
        showToast('info', '已重置', '表单已清空');
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        const totalEl = document.getElementById('totalCharts');
        if (totalEl) {
            totalEl.textContent = data.total || 0;
        }
    } catch (e) {
        console.log('加载统计失败');
    }
}

async function loadCharts() {
    const tbody = document.getElementById('chartList');
    if (!tbody) return;

    tbody.innerHTML = `
        <tr>
            <td colspan="6">
                <div class="empty-state">
                    <div class="spinner"></div>
                    <p>加载中...</p>
                </div>
            </td>
        </tr>
    `;

    try {
        const response = await fetch('/api/charts');
        const charts = await response.json();

        if (charts.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6">
                        <div class="empty-state">
                            <div class="icon">📊</div>
                            <h3>暂无图表</h3>
                            <p>开始创建您的第一个图表吧！</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = charts.map(chart => `
            <tr>
                <td><strong>#${chart.id}</strong></td>
                <td>${escapeHtml(chart.title)}</td>
                <td><span class="badge badge-${chart.chart_type}">${getChartTypeName(chart.chart_type)}</span></td>
                <td>${escapeHtml(chart.created_by)}</td>
                <td>${new Date(chart.created_at).toLocaleString('zh-CN')}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-primary" onclick="viewChart(${chart.id})">
                            👁️ 查看
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="empty-state">
                        <div class="icon">❌</div>
                        <h3>加载失败</h3>
                        <p>无法加载图表列表，请重试</p>
                    </div>
                </td>
            </tr>
        `;
    }
}

async function viewChart(id) {
    showLoading();

    try {
        const response = await fetch('/api/charts/' + id);
        const chart = await response.json();

        if (chart.error) {
            showToast('error', '加载失败', '未找到该图表');
            return;
        }

        const chartType = chart.chart_type;
        let xdata = chart.x_labels, ydata = chart.y_data, labels = chart.labels;

        const response2 = await fetch('/api/charts', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                title: chart.title + ' (预览)',
                chart_type: chartType,
                xdata, ydata, labels,
                created_by: chart.created_by
            })
        });

        const result = await response2.json();

        const chartDetail = document.getElementById('chartDetail');
        const chartView = document.getElementById('chartView');
        
        if (chartDetail) {
            chartDetail.innerHTML = `
                <p><strong>📝 标题:</strong> ${escapeHtml(chart.title)}</p>
                <p><strong>📊 类型:</strong> ${getChartTypeName(chartType)}</p>
                <p><strong>👤 创建者:</strong> ${escapeHtml(chart.created_by)}</p>
                <p><strong>🕐 创建时间:</strong> ${new Date(chart.created_at).toLocaleString('zh-CN')}</p>
                <img src="${result.image}" alt="图表" style="max-width: 100%; margin-top: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            `;
        }

        if (chartView) {
            chartView.style.display = 'block';
            chartView.scrollIntoView({behavior: 'smooth'});
        }

        showToast('success', '加载成功', '图表已生成预览');
    } catch (e) {
        showToast('error', '加载失败', '无法生成图表预览');
    } finally {
        hideLoading();
    }
}

let searchTimeout = null;

function handleSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        const keyword = document.getElementById('searchInput').value.trim();
        if (keyword.length >= 2) {
            searchCharts(keyword);
        } else if (keyword.length === 0) {
            loadCharts();
        }
    }, 300);
}

async function searchCharts(keyword) {
    const tbody = document.getElementById('chartList');
    if (!tbody) return;

    tbody.innerHTML = `
        <tr>
            <td colspan="6">
                <div class="empty-state">
                    <div class="spinner"></div>
                    <p>搜索中...</p>
                </div>
            </td>
        </tr>
    `;

    try {
        const response = await fetch(`/api/charts/search?q=${encodeURIComponent(keyword)}&limit=50`);
        const charts = await response.json();

        if (charts.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6">
                        <div class="empty-state">
                            <div class="icon">🔍</div>
                            <h3>未找到结果</h3>
                            <p>没有找到包含 "${escapeHtml(keyword)}" 的图表</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = charts.map(chart => `
            <tr>
                <td><strong>#${chart.id}</strong></td>
                <td>${escapeHtml(chart.title)}</td>
                <td><span class="badge badge-${chart.chart_type}">${getChartTypeName(chart.chart_type)}</span></td>
                <td>${escapeHtml(chart.created_by)}</td>
                <td>${new Date(chart.created_at).toLocaleString('zh-CN')}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-primary" onclick="viewChart(${chart.id})">
                            👁️ 查看
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        showToast('info', '搜索完成', `找到 ${charts.length} 个匹配的图表`);
    } catch (e) {
        showToast('error', '搜索失败', '无法执行搜索');
    }
}

function getChartTypeName(type) {
    const names = {
        'line': '📈 折线图',
        'bar': '📊 柱状图',
        'pie': '🥧 饼图'
    };
    return names[type] || type;
}

function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', login);
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', register);
    }

    const chartForm = document.getElementById('chartForm');
    if (chartForm) {
        chartForm.addEventListener('submit', createChart);
    }

    checkAuth();

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal('login');
            closeModal('register');
        }
    });

    document.querySelectorAll('.modal-overlay').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });
});
