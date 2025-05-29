// 创建Vue应用
const { createApp, ref, onMounted, reactive } = Vue;

const app = createApp({
    setup() {
        // 身份验证相关
        const isAuthenticated = ref(false);
        const currentUser = ref({});
        const loginForm = reactive({
            username: '',
            password: ''
        });
        const loginError = ref('');

        // 模块切换
        const activeModule = ref('student');

        // 学生管理相关
        const students = ref([]);
        const studentTotal = ref(0);
        const studentPage = ref(1);
        const studentSearch = ref('');
        const classes = ref([]);
        const colleges = ref([]);
        const studentForm = reactive({
            student_no: '',
            name: '',
            gender: '男',
            birth_date: '',
            id_card: '',
            enrollment_date: '',
            class_id: '',
            address: '',
            phone: '',
            email: '',
            status: '在读'
        });
        const editingStudentId = ref(null);

        // 教师管理相关
        const teachers = ref([]);
        const teacherTotal = ref(0);
        const teacherPage = ref(1);
        const teacherSearch = ref('');
        const titles = ref([]);

        // 课程管理相关
        const courses = ref([]);
        const courseTotal = ref(0);
        const coursePage = ref(1);
        const courseSearch = ref('');
        const courseTypes = ref([]);

        // 授课管理相关
        const offerings = ref([]);
        const offeringTotal = ref(0);
        const offeringPage = ref(1);
        const offeringSearch = ref('');

        // 成绩管理相关
        const scores = ref([]);
        const scoreTotal = ref(0);
        const scorePage = ref(1);
        const scoreSearch = ref('');

        // 校验登录状态
        const checkAuth = async () => {
            try {
                const response = await axios.get('/api/auth/check_auth');
                if (response.data.authenticated) {
                    isAuthenticated.value = true;
                    currentUser.value = response.data.user;
                }
            } catch (error) {
                console.error('验证登录状态失败:', error);
            }
        };

        // 登录
        const login = async () => {
            try {
                const response = await axios.post('/api/auth/login', loginForm);
                if (response.data.success) {
                    isAuthenticated.value = true;
                    currentUser.value = response.data.user;
                    loginError.value = '';
                    // 加载初始数据
                    await loadStudents();
                    await loadClasses();
                    await loadColleges();
                }
            } catch (error) {
                loginError.value = error.response?.data?.error || '登录失败，请稍后重试';
                console.error('登录失败:', error);
            }
        };

        // 登出
        const logout = async () => {
            try {
                await axios.post('/api/auth/logout');
                isAuthenticated.value = false;
                currentUser.value = {};
            } catch (error) {
                console.error('登出失败:', error);
            }
        };

        // 切换模块
        const activateModule = (moduleName) => {
            activeModule.value = moduleName;
            
            // 根据模块加载数据
            switch (moduleName) {
                case 'student':
                    loadStudents();
                    loadClasses();
                    break;
                case 'teacher':
                    loadTeachers();
                    loadTitles();
                    loadColleges();
                    break;
                case 'course':
                    loadCourses();
                    loadCourseTypes();
                    loadColleges();
                    break;
                case 'offering':
                    loadOfferings();
                    loadCourses();
                    loadTeachers();
                    break;
                case 'score':
                    // 根据需要加载数据
                    break;
            }
        };

        // 分页切换
        const changePage = (page, type) => {
            if (page < 1) return;
            
            switch (type) {
                case 'student':
                    studentPage.value = page;
                    loadStudents();
                    break;
                case 'teacher':
                    teacherPage.value = page;
                    loadTeachers();
                    break;
                case 'course':
                    coursePage.value = page;
                    loadCourses();
                    break;
                case 'offering':
                    offeringPage.value = page;
                    loadOfferings();
                    break;
                case 'score':
                    scorePage.value = page;
                    // 加载成绩数据
                    break;
            }
        };

        // 学生管理相关函数
        const loadStudents = async () => {
            try {
                const response = await axios.get(`/api/student/?page=${studentPage.value}&search=${studentSearch.value}`);
                students.value = response.data.students;
                studentTotal.value = response.data.total;
            } catch (error) {
                console.error('加载学生数据失败:', error);
            }
        };

        const searchStudents = () => {
            studentPage.value = 1;
            loadStudents();
        };

        const loadClasses = async () => {
            try {
                const response = await axios.get('/api/student/class');
                classes.value = response.data.classes;
            } catch (error) {
                console.error('加载班级数据失败:', error);
            }
        };

        const loadColleges = async () => {
            try {
                const response = await axios.get('/api/student/college');
                colleges.value = response.data.colleges;
            } catch (error) {
                console.error('加载学院数据失败:', error);
            }
        };

        const resetStudentForm = () => {
            Object.assign(studentForm, {
                student_no: '',
                name: '',
                gender: '男',
                birth_date: '',
                id_card: '',
                enrollment_date: '',
                class_id: '',
                address: '',
                phone: '',
                email: '',
                status: '在读'
            });
            editingStudentId.value = null;
        };

        const saveStudent = async () => {
            try {
                await axios.post('/api/student/', studentForm);
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('addStudentModal'));
                modal.hide();
                // 重新加载学生数据
                await loadStudents();
                // 重置表单
                resetStudentForm();
            } catch (error) {
                console.error('添加学生失败:', error);
                alert(error.response?.data?.error || '添加学生失败，请稍后重试');
            }
        };

        const viewStudent = async (studentId) => {
            try {
                const response = await axios.get(`/api/student/${studentId}`);
                // 显示学生详情
                alert(`学生详情: ${JSON.stringify(response.data.student)}`);
            } catch (error) {
                console.error('获取学生详情失败:', error);
            }
        };

        const editStudent = async (studentId) => {
            try {
                const response = await axios.get(`/api/student/${studentId}`);
                // 填充表单
                Object.assign(studentForm, response.data.student);
                editingStudentId.value = studentId;
                
                // 打开编辑模态框
                const modal = new bootstrap.Modal(document.getElementById('editStudentModal'));
                modal.show();
            } catch (error) {
                console.error('获取学生信息失败:', error);
            }
        };

        const updateStudent = async () => {
            if (!editingStudentId.value) return;
            
            try {
                await axios.put(`/api/student/${editingStudentId.value}`, studentForm);
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('editStudentModal'));
                modal.hide();
                // 重新加载学生数据
                await loadStudents();
                // 重置表单
                resetStudentForm();
            } catch (error) {
                console.error('更新学生失败:', error);
                alert(error.response?.data?.error || '更新学生失败，请稍后重试');
            }
        };

        const confirmDeleteStudent = (studentId) => {
            if (confirm('确定要删除这个学生吗？')) {
                deleteStudent(studentId);
            }
        };

        const deleteStudent = async (studentId) => {
            try {
                await axios.delete(`/api/student/${studentId}`);
                // 重新加载学生数据
                await loadStudents();
            } catch (error) {
                console.error('删除学生失败:', error);
                alert(error.response?.data?.error || '删除学生失败，请稍后重试');
            }
        };

        // 教师管理相关函数
        const loadTeachers = async () => {
            try {
                const response = await axios.get(`/api/teacher/?page=${teacherPage.value}&search=${teacherSearch.value}`);
                teachers.value = response.data.teachers;
                teacherTotal.value = response.data.total;
            } catch (error) {
                console.error('加载教师数据失败:', error);
            }
        };

        const loadTitles = async () => {
            try {
                const response = await axios.get('/api/teacher/title');
                titles.value = response.data.titles;
            } catch (error) {
                console.error('加载职称数据失败:', error);
            }
        };

        // 课程管理相关函数
        const loadCourses = async () => {
            try {
                const response = await axios.get(`/api/course/?page=${coursePage.value}&search=${courseSearch.value}`);
                courses.value = response.data.courses;
                courseTotal.value = response.data.total;
            } catch (error) {
                console.error('加载课程数据失败:', error);
            }
        };

        const loadCourseTypes = async () => {
            try {
                const response = await axios.get('/api/course/type');
                courseTypes.value = response.data.course_types;
            } catch (error) {
                console.error('加载课程类型数据失败:', error);
            }
        };

        // 授课管理相关函数
        const loadOfferings = async () => {
            try {
                const response = await axios.get(`/api/offering/?page=${offeringPage.value}&search=${offeringSearch.value}`);
                offerings.value = response.data.offerings;
                offeringTotal.value = response.data.total;
            } catch (error) {
                console.error('加载授课安排数据失败:', error);
            }
        };

        // 在组件挂载时检查登录状态
        onMounted(() => {
            checkAuth();
        });

        return {
            // 身份验证相关
            isAuthenticated,
            currentUser,
            loginForm,
            loginError,
            login,
            logout,
            
            // 模块切换
            activeModule,
            activateModule,
            
            // 分页
            changePage,
            
            // 学生管理相关
            students,
            studentTotal,
            studentPage,
            studentSearch,
            classes,
            colleges,
            studentForm,
            searchStudents,
            saveStudent,
            viewStudent,
            editStudent,
            updateStudent,
            confirmDeleteStudent,
            
            // 教师管理相关
            teachers,
            teacherTotal,
            teacherPage,
            teacherSearch,
            titles,
            
            // 课程管理相关
            courses,
            courseTotal,
            coursePage,
            courseSearch,
            courseTypes,
            
            // 授课管理相关
            offerings,
            offeringTotal,
            offeringPage,
            offeringSearch,
            
            // 成绩管理相关
            scores,
            scoreTotal,
            scorePage,
            scoreSearch
        };
    }
});

// 挂载应用
app.mount('#app'); 