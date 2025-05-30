// 创建Vue应用
const { createApp, ref, onMounted, reactive, computed, watch } = Vue;

// 添加通用的日期格式化函数
function formatDateForInput(dateString) {
    if (!dateString) return '';
    
    try {
        // 处理常见格式
        let date;
        if (dateString.includes('T')) {
            // ISO格式 (YYYY-MM-DDTHH:mm:ss.sssZ)
            date = new Date(dateString);
        } else if (dateString.includes('/')) {
            // YYYY/MM/DD格式
            const parts = dateString.split('/');
            date = new Date(parts[0], parts[1] - 1, parts[2]);
        } else if (dateString.includes('-')) {
            // YYYY-MM-DD格式
            date = new Date(dateString);
        } else {
            // 尝试作为时间戳处理
            date = new Date(Number(dateString));
        }
        
        // 检查日期是否有效
        if (isNaN(date.getTime())) {
            console.error('无效的日期:', dateString);
            return '';
        }
        
        // 格式化为YYYY-MM-DD (HTML input[type=date]需要的格式)
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        
        return `${year}-${month}-${day}`;
    } catch (e) {
        console.error('日期格式化错误:', e);
        return '';
    }
}

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
        
        // 详情查看
        const viewingStudent = ref(null);
        const viewingTeacher = ref(null);
        const viewingCourse = ref(null);
        const viewingOffering = ref(null);
        
        // 搜索过滤
        const courseFilter = ref('');
        const teacherFilter = ref('');
        const offeringFilter = ref('');

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
        const teacherForm = reactive({
            teacher_no: '',
            name: '',
            gender: '男',
            birth_date: '',
            title_id: '',
            college_id: '',
            phone: '',
            email: ''
        });
        const editingTeacherId = ref(null);

        // 课程管理相关
        const courses = ref([]);
        const courseTotal = ref(0);
        const coursePage = ref(1);
        const courseSearch = ref('');
        const courseTypes = ref([]);
        const courseForm = reactive({
            course_code: '',
            course_name: '',
            credit: 3.0,
            hours: 48,
            type_id: '',
            college_id: ''
        });
        const editingCourseId = ref(null);

        // 授课管理相关
        const offerings = ref([]);
        const offeringTotal = ref(0);
        const offeringPage = ref(1);
        const offeringSearch = ref('');
        const offeringForm = reactive({
            course_id: '',
            teacher_id: '',
            semester: '春季',
            year: new Date().getFullYear(),
            classroom: '',
            class_time: ''
        });
        const editingOfferingId = ref(null);

        // 成绩管理相关
        const scores = ref([]);
        const scoreTotal = ref(0);
        const scorePage = ref(1);
        const scoreSearch = ref('');
        const selectedStudentId = ref('');
        const selectedStudentInfo = ref(null);
        const scoreForm = reactive({
            student_id: '',
            offering_id: '',
            score: '',
            status: '选课中'
        });
        const editingScoreId = ref(null);
        const allScores = ref([]);
        const scoreFilter = ref('');
        
        // 成绩统计
        const totalCredits = computed(() => {
            let total = 0;
            scores.value.forEach(score => {
                if (score.status === '已修完') {
                    total += parseFloat(score.credit);
                }
            });
            return total.toFixed(1);
        });

        const averageScore = computed(() => {
            let total = 0;
            let count = 0;
            scores.value.forEach(score => {
                if (score.status === '已修完' && score.score) {
                    total += parseFloat(score.score);
                    count++;
                }
            });
            return count > 0 ? (total / count).toFixed(2) : '暂无';
        });

        const completedCourses = computed(() => {
            return scores.value.filter(score => score.status === '已修完').length;
        });
        
        // 过滤后的列表
        const filteredCourses = computed(() => {
            if (!courseFilter.value) return courses.value;
            const filter = courseFilter.value.toLowerCase();
            return courses.value.filter(course => 
                course.course_name.toLowerCase().includes(filter) || 
                course.course_code.toLowerCase().includes(filter)
            );
        });

        const filteredTeachers = computed(() => {
            if (!teacherFilter.value) return teachers.value;
            const filter = teacherFilter.value.toLowerCase();
            return teachers.value.filter(teacher => 
                teacher.name.toLowerCase().includes(filter) || 
                teacher.teacher_no.toLowerCase().includes(filter)
            );
        });

        const filteredOfferings = computed(() => {
            if (!offeringFilter.value) return offerings.value;
            const filter = offeringFilter.value.toLowerCase();
            return offerings.value.filter(offering => 
                offering.course_name.toLowerCase().includes(filter) || 
                offering.teacher_name.toLowerCase().includes(filter) ||
                offering.course_code.toLowerCase().includes(filter) ||
                (offering.year + '年' + offering.semester).toLowerCase().includes(filter)
            );
        });

        // 添加filteredScores计算属性
        const filteredScores = computed(() => {
            if (!scoreFilter.value) return scores.value;
            const filter = scoreFilter.value.toLowerCase();
            return scores.value.filter(score => 
                score.course_name.toLowerCase().includes(filter) || 
                score.teacher_name.toLowerCase().includes(filter)
            );
        });

        // 班级管理相关
        const classTabActive = ref('class'); // 默认显示班级管理标签
        const classSearch = ref('');
        const collegeSearch = ref('');
        const classForm = reactive({
            class_name: '',
            class_code: '',
            college_id: '',
            admission_year: new Date().getFullYear()
        });
        const collegeForm = reactive({
            college_name: '',
            college_code: ''
        });
        const editingClassId = ref(null);
        const editingCollegeId = ref(null);
        
        // 学院排序相关
        const collegeSortField = ref('college_name');
        const collegeSortOrder = ref('asc');
        
        // 过滤后的班级列表
        const filteredClasses = computed(() => {
            if (!classSearch.value) return classes.value;
            const filter = classSearch.value.toLowerCase();
            return classes.value.filter(cls => 
                cls.class_name.toLowerCase().includes(filter) || 
                cls.class_code.toLowerCase().includes(filter) ||
                cls.college_name.toLowerCase().includes(filter)
            );
        });
        
        // 过滤后的学院列表
        const filteredColleges = computed(() => {
            if (!collegeSearch.value) return colleges.value;
            const filter = collegeSearch.value.toLowerCase();
            return colleges.value.filter(college => 
                college.college_name.toLowerCase().includes(filter) || 
                (college.college_code && college.college_code.toLowerCase().includes(filter))
            );
        });
        
        // 排序后的学院列表
        const sortedColleges = computed(() => {
            return [...filteredColleges.value].sort((a, b) => {
                const fieldA = a[collegeSortField.value];
                const fieldB = b[collegeSortField.value];
                
                // 处理数字字段特殊情况
                if (!isNaN(Number(fieldA)) && !isNaN(Number(fieldB))) {
                    return collegeSortOrder.value === 'asc' 
                        ? Number(fieldA) - Number(fieldB) 
                        : Number(fieldB) - Number(fieldA);
                }
                
                // 普通字符串比较
                const compareResult = String(fieldA).localeCompare(String(fieldB));
                return collegeSortOrder.value === 'asc' ? compareResult : -compareResult;
            });
        });
        
        const resetCollegeForm = () => {
            Object.assign(collegeForm, {
                college_name: '',
                college_code: ''
            });
            editingCollegeId.value = null;
        };
        
        const saveCollege = async () => {
            try {
                await axios.post('/api/student/college', collegeForm);
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('addCollegeModal'));
                modal.hide();
                // 重新加载学院数据
                await loadColleges();
                // 重置表单
                resetCollegeForm();
                alert('学院添加成功');
            } catch (error) {
                console.error('添加学院失败:', error);
                alert(error.response?.data?.error || '添加学院失败，请稍后重试');
            }
        };
        
        const editCollege = async (collegeId) => {
            try {
                const response = await axios.get(`/api/student/college/${collegeId}`);
                // 填充表单
                Object.assign(collegeForm, response.data.college);
                editingCollegeId.value = collegeId;
                
                // 打开编辑模态框
                const modal = new bootstrap.Modal(document.getElementById('editCollegeModal'));
                modal.show();
            } catch (error) {
                console.error('获取学院信息失败:', error);
            }
        };
        
        const updateCollege = async () => {
            if (!editingCollegeId.value) return;
            
            try {
                await axios.put(`/api/student/college/${editingCollegeId.value}`, collegeForm);
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('editCollegeModal'));
                modal.hide();
                // 重新加载学院数据
                await loadColleges();
                // 重置表单
                resetCollegeForm();
                alert('学院更新成功');
            } catch (error) {
                console.error('更新学院失败:', error);
                alert(error.response?.data?.error || '更新学院失败，请稍后重试');
            }
        };
        
        const confirmDeleteCollege = (collegeId) => {
            if (confirm('确定要删除这个学院吗？这可能会影响到已关联该学院的班级和教师。')) {
                deleteCollege(collegeId);
            }
        };
        
        const deleteCollege = async (collegeId) => {
            try {
                await axios.delete(`/api/student/college/${collegeId}`);
                // 重新加载学院数据
                await loadColleges();
                alert('学院删除成功');
            } catch (error) {
                console.error('删除学院失败:', error);
                alert(error.response?.data?.error || '删除学院失败，请稍后重试');
            }
        };

        // 排序相关
        const studentSortField = ref('student_no');
        const studentSortOrder = ref('asc');
        const teacherSortField = ref('teacher_no');
        const teacherSortOrder = ref('asc');
        const classSortField = ref('class_code');
        const classSortOrder = ref('asc');
        const courseSortField = ref('course_code');
        const courseSortOrder = ref('asc');
        const offeringSortField = ref('year');
        const offeringSortOrder = ref('desc');
        
        // 切换排序顺序
        const toggleSort = (module, field) => {
            switch (module) {
                case 'student':
                    if (studentSortField.value === field) {
                        studentSortOrder.value = studentSortOrder.value === 'asc' ? 'desc' : 'asc';
                    } else {
                        studentSortField.value = field;
                        studentSortOrder.value = 'asc';
                    }
                    break;
                case 'teacher':
                    if (teacherSortField.value === field) {
                        teacherSortOrder.value = teacherSortOrder.value === 'asc' ? 'desc' : 'asc';
                    } else {
                        teacherSortField.value = field;
                        teacherSortOrder.value = 'asc';
                    }
                    break;
                case 'class':
                    if (classSortField.value === field) {
                        classSortOrder.value = classSortOrder.value === 'asc' ? 'desc' : 'asc';
                    } else {
                        classSortField.value = field;
                        classSortOrder.value = 'asc';
                    }
                    break;
                case 'course':
                    if (courseSortField.value === field) {
                        courseSortOrder.value = courseSortOrder.value === 'asc' ? 'desc' : 'asc';
                    } else {
                        courseSortField.value = field;
                        courseSortOrder.value = 'asc';
                    }
                    break;
                case 'offering':
                    if (offeringSortField.value === field) {
                        offeringSortOrder.value = offeringSortOrder.value === 'asc' ? 'desc' : 'asc';
                    } else {
                        offeringSortField.value = field;
                        offeringSortOrder.value = 'asc';
                    }
                    break;
            }
        };
        
        // 获取排序图标
        const getSortIcon = (module, field) => {
            let currentField, currentOrder;
            
            switch (module) {
                case 'student':
                    currentField = studentSortField.value;
                    currentOrder = studentSortOrder.value;
                    break;
                case 'teacher':
                    currentField = teacherSortField.value;
                    currentOrder = teacherSortOrder.value;
                    break;
                case 'class':
                    currentField = classSortField.value;
                    currentOrder = classSortOrder.value;
                    break;
                case 'course':
                    currentField = courseSortField.value;
                    currentOrder = courseSortOrder.value;
                    break;
                case 'offering':
                    currentField = offeringSortField.value;
                    currentOrder = offeringSortOrder.value;
                    break;
            }
            
            if (currentField !== field) {
                return 'bi-arrow-down-up text-muted';
            } else if (currentOrder === 'asc') {
                return 'bi-sort-down text-primary';
            } else {
                return 'bi-sort-up text-primary';
            }
        };
        
        // 对数据进行排序的计算属性
        const sortedStudents = computed(() => {
            return [...students.value].sort((a, b) => {
                const fieldA = a[studentSortField.value];
                const fieldB = b[studentSortField.value];
                
                // 处理数字字段特殊情况
                if (!isNaN(Number(fieldA)) && !isNaN(Number(fieldB))) {
                    return studentSortOrder.value === 'asc' 
                        ? Number(fieldA) - Number(fieldB) 
                        : Number(fieldB) - Number(fieldA);
                }
                
                // 普通字符串比较
                const compareResult = String(fieldA).localeCompare(String(fieldB));
                return studentSortOrder.value === 'asc' ? compareResult : -compareResult;
            });
        });
        
        const sortedTeachers = computed(() => {
            return [...teachers.value].sort((a, b) => {
                const fieldA = a[teacherSortField.value];
                const fieldB = b[teacherSortField.value];
                
                // 处理数字字段特殊情况
                if (!isNaN(Number(fieldA)) && !isNaN(Number(fieldB))) {
                    return teacherSortOrder.value === 'asc' 
                        ? Number(fieldA) - Number(fieldB) 
                        : Number(fieldB) - Number(fieldA);
                }
                
                // 普通字符串比较
                const compareResult = String(fieldA).localeCompare(String(fieldB));
                return teacherSortOrder.value === 'asc' ? compareResult : -compareResult;
            });
        });
        
        const sortedClasses = computed(() => {
            return [...classes.value].sort((a, b) => {
                const fieldA = a[classSortField.value];
                const fieldB = b[classSortField.value];
                
                // 处理数字字段特殊情况
                if (!isNaN(Number(fieldA)) && !isNaN(Number(fieldB))) {
                    return classSortOrder.value === 'asc' 
                        ? Number(fieldA) - Number(fieldB) 
                        : Number(fieldB) - Number(fieldA);
                }
                
                // 普通字符串比较
                const compareResult = String(fieldA).localeCompare(String(fieldB));
                return classSortOrder.value === 'asc' ? compareResult : -compareResult;
            });
        });
        
        const sortedCourses = computed(() => {
            return [...courses.value].sort((a, b) => {
                const fieldA = a[courseSortField.value];
                const fieldB = b[courseSortField.value];
                
                // 处理数字字段特殊情况
                if (!isNaN(Number(fieldA)) && !isNaN(Number(fieldB))) {
                    return courseSortOrder.value === 'asc' 
                        ? Number(fieldA) - Number(fieldB) 
                        : Number(fieldB) - Number(fieldA);
                }
                
                // 普通字符串比较
                const compareResult = String(fieldA).localeCompare(String(fieldB));
                return courseSortOrder.value === 'asc' ? compareResult : -compareResult;
            });
        });
        
        const sortedOfferings = computed(() => {
            return [...offerings.value].sort((a, b) => {
                const fieldA = a[offeringSortField.value];
                const fieldB = b[offeringSortField.value];
                
                // 处理数字字段特殊情况
                if (!isNaN(Number(fieldA)) && !isNaN(Number(fieldB))) {
                    return offeringSortOrder.value === 'asc' 
                        ? Number(fieldA) - Number(fieldB) 
                        : Number(fieldB) - Number(fieldA);
                }
                
                // 普通字符串比较
                const compareResult = String(fieldA).localeCompare(String(fieldB));
                return offeringSortOrder.value === 'asc' ? compareResult : -compareResult;
            });
        });
        
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
                    loadColleges();
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
                    loadStudents();
                    loadOfferings();
                    break;
                case 'class':
                    loadClasses();
                    loadColleges();
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

        // 添加防抖函数
        const debounce = (fn, delay) => {
            let timer = null;
            return function (...args) {
                if (timer) clearTimeout(timer);
                timer = setTimeout(() => {
                    fn.apply(this, args);
                }, delay);
            };
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

        // 使用 watch 监听搜索输入，实现实时搜索
        watch(studentSearch, debounce(() => {
            studentPage.value = 1;
            loadStudents();
        }, 300));

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
            const today = new Date().toISOString().split('T')[0]; // 获取当天日期，格式为YYYY-MM-DD
            Object.assign(studentForm, {
                student_no: '',
                name: '',
                gender: '男',
                birth_date: '',
                id_card: '',
                enrollment_date: today, // 默认为当天
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
                // 检查权限
                if (currentUser.value.role !== 'admin') {
                    alert('您没有管理员权限，无法添加学生');
                    return;
                }
                
                console.log('保存学生数据:', studentForm);
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
                if (error.response?.status === 403) {
                    alert('您没有权限执行此操作');
                } else {
                    alert(error.response?.data?.error || '添加学生失败，请稍后重试');
                }
            }
        };

        const viewStudent = async (studentId) => {
            try {
                const response = await axios.get(`/api/student/${studentId}`);
                // 设置查看的学生数据
                viewingStudent.value = response.data.student;
                
                // 使用新的方法更新模态框内容
                updateStudentModalContent(response.data.student);
                
                // 打开模态框
                const modal = new bootstrap.Modal(document.getElementById('viewStudentModal'));
                modal.show();
            } catch (error) {
                console.error('获取学生详情失败:', error);
                alert('获取学生详情失败，请稍后重试');
            }
        };

        const editStudent = async (studentId) => {
            try {
                const response = await axios.get(`/api/student/${studentId}`);
                // 填充表单
                const studentData = {...response.data.student};
                
                // 处理日期格式
                studentData.birth_date = formatDateForInput(studentData.birth_date);
                studentData.enrollment_date = formatDateForInput(studentData.enrollment_date);
                
                Object.assign(studentForm, studentData);
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
                // 检查权限
                if (currentUser.value.role !== 'admin') {
                    alert('您没有管理员权限，无法修改学生信息');
                    return;
                }
                
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
                if (error.response?.status === 403) {
                    alert('您没有权限执行此操作');
                } else {
                    alert(error.response?.data?.error || '更新学生失败，请稍后重试');
                }
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

        // 实时搜索教师
        watch(teacherSearch, debounce(() => {
            teacherPage.value = 1;
            loadTeachers();
        }, 300));

        const searchTeachers = () => {
            teacherPage.value = 1;
            loadTeachers();
        };

        const loadTitles = async () => {
            try {
                const response = await axios.get('/api/teacher/title');
                titles.value = response.data.titles;
            } catch (error) {
                console.error('加载职称数据失败:', error);
            }
        };

        const resetTeacherForm = () => {
            const today = new Date().toISOString().split('T')[0]; // 获取当天日期，格式为YYYY-MM-DD
            Object.assign(teacherForm, {
                teacher_no: '',
                name: '',
                gender: '男',
                birth_date: today, // 默认为当天
                title_id: '',
                college_id: '',
                phone: '',
                email: ''
            });
            editingTeacherId.value = null;
        };

        const saveTeacher = async () => {
            try {
                // 检查权限
                if (currentUser.value.role !== 'admin') {
                    alert('您没有管理员权限，无法添加教师');
                    return;
                }
                
                console.log('保存教师数据:', teacherForm);
                await axios.post('/api/teacher/', teacherForm);
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('addTeacherModal'));
                modal.hide();
                // 重新加载教师数据
                await loadTeachers();
                // 重置表单
                resetTeacherForm();
            } catch (error) {
                console.error('添加教师失败:', error);
                if (error.response?.status === 403) {
                    alert('您没有权限执行此操作');
                } else {
                    alert(error.response?.data?.error || '添加教师失败，请稍后重试');
                }
            }
        };

        const viewTeacher = async (teacherId) => {
            try {
                const response = await axios.get(`/api/teacher/${teacherId}`);
                // 设置查看的教师数据
                viewingTeacher.value = response.data.teacher;
                
                // 使用新的方法更新模态框内容
                updateTeacherModalContent(response.data.teacher);
                
                // 打开模态框
                const modal = new bootstrap.Modal(document.getElementById('viewTeacherModal'));
                modal.show();
            } catch (error) {
                console.error('获取教师详情失败:', error);
                alert('获取教师详情失败，请稍后重试');
            }
        };

        const editTeacher = async (teacherId) => {
            try {
                const response = await axios.get(`/api/teacher/${teacherId}`);
                // 填充表单
                const teacherData = {...response.data.teacher};
                
                // 处理日期格式
                teacherData.birth_date = formatDateForInput(teacherData.birth_date);
                
                Object.assign(teacherForm, teacherData);
                editingTeacherId.value = teacherId;
                
                // 打开编辑模态框
                const modal = new bootstrap.Modal(document.getElementById('editTeacherModal'));
                modal.show();
            } catch (error) {
                console.error('获取教师信息失败:', error);
            }
        };

        const updateTeacher = async () => {
            if (!editingTeacherId.value) return;
            
            try {
                // 检查权限
                if (currentUser.value.role !== 'admin') {
                    alert('您没有管理员权限，无法修改教师信息');
                    return;
                }
                
                await axios.put(`/api/teacher/${editingTeacherId.value}`, teacherForm);
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('editTeacherModal'));
                modal.hide();
                // 重新加载教师数据
                await loadTeachers();
                // 重置表单
                resetTeacherForm();
            } catch (error) {
                console.error('更新教师失败:', error);
                if (error.response?.status === 403) {
                    alert('您没有权限执行此操作');
                } else {
                    alert(error.response?.data?.error || '更新教师失败，请稍后重试');
                }
            }
        };

        const confirmDeleteTeacher = (teacherId) => {
            if (confirm('确定要删除这个教师吗？')) {
                deleteTeacher(teacherId);
            }
        };

        const deleteTeacher = async (teacherId) => {
            try {
                await axios.delete(`/api/teacher/${teacherId}`);
                // 重新加载教师数据
                await loadTeachers();
            } catch (error) {
                console.error('删除教师失败:', error);
                alert(error.response?.data?.error || '删除教师失败，请稍后重试');
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

        // 实时搜索课程
        watch(courseSearch, debounce(() => {
            coursePage.value = 1;
            loadCourses();
        }, 300));

        const searchCourses = () => {
            coursePage.value = 1;
            loadCourses();
        };

        const loadCourseTypes = async () => {
            try {
                const response = await axios.get('/api/course/type');
                courseTypes.value = response.data.course_types;
            } catch (error) {
                console.error('加载课程类型数据失败:', error);
            }
        };

        const resetCourseForm = () => {
            Object.assign(courseForm, {
                course_code: '',
                course_name: '',
                credit: 3.0,
                hours: 48,
                type_id: '',
                college_id: ''
            });
            editingCourseId.value = null;
        };

        const saveCourse = async () => {
            try {
                await axios.post('/api/course/', courseForm);
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('addCourseModal'));
                modal.hide();
                // 重新加载课程数据
                await loadCourses();
                // 重置表单
                resetCourseForm();
            } catch (error) {
                console.error('添加课程失败:', error);
                alert(error.response?.data?.error || '添加课程失败，请稍后重试');
            }
        };

        const viewCourse = async (courseId) => {
            try {
                const response = await axios.get(`/api/course/${courseId}`);
                // 设置查看的课程数据
                viewingCourse.value = response.data.course;
                
                // 使用新的方法更新模态框内容
                updateCourseModalContent(response.data.course);
                
                // 打开模态框
                const modal = new bootstrap.Modal(document.getElementById('viewCourseModal'));
                modal.show();
            } catch (error) {
                console.error('获取课程详情失败:', error);
                alert('获取课程详情失败，请稍后重试');
            }
        };

        const editCourse = async (courseId) => {
            try {
                const response = await axios.get(`/api/course/${courseId}`);
                // 填充表单
                Object.assign(courseForm, response.data.course);
                editingCourseId.value = courseId;
                
                // 打开编辑模态框
                const modal = new bootstrap.Modal(document.getElementById('editCourseModal'));
                modal.show();
            } catch (error) {
                console.error('获取课程信息失败:', error);
            }
        };

        const updateCourse = async () => {
            if (!editingCourseId.value) return;
            
            try {
                await axios.put(`/api/course/${editingCourseId.value}`, courseForm);
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('editCourseModal'));
                modal.hide();
                // 重新加载课程数据
                await loadCourses();
                // 重置表单
                resetCourseForm();
            } catch (error) {
                console.error('更新课程失败:', error);
                alert(error.response?.data?.error || '更新课程失败，请稍后重试');
            }
        };

        const confirmDeleteCourse = (courseId) => {
            if (confirm('确定要删除这个课程吗？')) {
                deleteCourse(courseId);
            }
        };

        const deleteCourse = async (courseId) => {
            try {
                await axios.delete(`/api/course/${courseId}`);
                // 重新加载课程数据
                await loadCourses();
            } catch (error) {
                console.error('删除课程失败:', error);
                alert(error.response?.data?.error || '删除课程失败，请稍后重试');
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

        // 实时搜索授课安排
        watch(offeringSearch, debounce(() => {
            offeringPage.value = 1;
            loadOfferings();
        }, 300));

        const searchOfferings = () => {
            offeringPage.value = 1;
            loadOfferings();
        };

        const resetOfferingForm = () => {
            Object.assign(offeringForm, {
                course_id: '',
                teacher_id: '',
                semester: '春季',
                year: new Date().getFullYear(),
                classroom: '',
                class_time: ''
            });
            editingOfferingId.value = null;
        };

        const saveOffering = async () => {
            try {
                await axios.post('/api/offering/', offeringForm);
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('addOfferingModal'));
                modal.hide();
                // 重新加载授课安排数据
                await loadOfferings();
                // 重置表单
                resetOfferingForm();
            } catch (error) {
                console.error('添加授课安排失败:', error);
                alert(error.response?.data?.error || '添加授课安排失败，请稍后重试');
            }
        };

        const viewOffering = async (offeringId) => {
            try {
                const response = await axios.get(`/api/offering/${offeringId}`);
                // 设置查看的授课安排数据
                viewingOffering.value = response.data.offering;
                
                // 使用新的方法更新模态框内容
                updateOfferingModalContent(response.data.offering);
                
                // 打开模态框
                const modal = new bootstrap.Modal(document.getElementById('viewOfferingModal'));
                modal.show();
            } catch (error) {
                console.error('获取授课安排详情失败:', error);
                alert('获取授课安排详情失败，请稍后重试');
            }
        };

        const editOffering = async (offeringId) => {
            try {
                const response = await axios.get(`/api/offering/${offeringId}`);
                // 填充表单
                Object.assign(offeringForm, response.data.offering);
                editingOfferingId.value = offeringId;
                
                // 打开编辑模态框
                const modal = new bootstrap.Modal(document.getElementById('editOfferingModal'));
                modal.show();
            } catch (error) {
                console.error('获取授课安排信息失败:', error);
            }
        };

        const updateOffering = async () => {
            if (!editingOfferingId.value) return;
            
            try {
                await axios.put(`/api/offering/${editingOfferingId.value}`, offeringForm);
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('editOfferingModal'));
                modal.hide();
                // 重新加载授课安排数据
                await loadOfferings();
                // 重置表单
                resetOfferingForm();
            } catch (error) {
                console.error('更新授课安排失败:', error);
                alert(error.response?.data?.error || '更新授课安排失败，请稍后重试');
            }
        };

        const confirmDeleteOffering = (offeringId) => {
            if (confirm('确定要删除这个授课安排吗？')) {
                deleteOffering(offeringId);
            }
        };

        const deleteOffering = async (offeringId) => {
            try {
                await axios.delete(`/api/offering/${offeringId}`);
                // 重新加载授课安排数据
                await loadOfferings();
            } catch (error) {
                console.error('删除授课安排失败:', error);
                alert(error.response?.data?.error || '删除授课安排失败，请稍后重试');
            }
        };

        // 成绩管理相关函数
        const searchScores = () => {
            // 搜索学生功能
            studentPage.value = 1;
            studentSearch.value = scoreSearch.value;
            loadStudents();
        };

        const loadStudentScores = async (studentId) => {
            if (studentId) {
                selectedStudentId.value = studentId;
                
                // 加载学生信息
                try {
                    const response = await axios.get(`/api/student/${studentId}`);
                    selectedStudentInfo.value = response.data.student;
                } catch (error) {
                    console.error('加载学生信息失败:', error);
                    selectedStudentInfo.value = null;
                }
            }
            
            if (!selectedStudentId.value) return;
            
            // 清空过滤条件
            scoreFilter.value = '';
            
            // 加载成绩
            try {
                const response = await axios.get(`/api/score/${selectedStudentId.value}`);
                scores.value = response.data.scores;
                allScores.value = [...response.data.scores]; // 保存完整列表用于搜索
            } catch (error) {
                console.error('加载学生成绩数据失败:', error);
            }
        };

        const filterScores = () => {
            // 使用计算属性filteredScores，无需额外处理
            // 这个函数主要用于搜索按钮的点击事件
        };

        const resetScoreForm = () => {
            Object.assign(scoreForm, {
                student_id: selectedStudentId.value || '',
                offering_id: '',
                score: '',
                status: '选课中'
            });
            editingScoreId.value = null;
        };

        const saveScore = async () => {
            try {
                // 确保必要字段存在
                if (!scoreForm.student_id || !scoreForm.offering_id || !scoreForm.status) {
                    alert('请选择学生、课程和状态');
                    return;
                }
                
                // 如果状态是已修完，确保有成绩
                if (scoreForm.status === '已修完' && (!scoreForm.score || scoreForm.score === '')) {
                    alert('已修完状态需要填写成绩');
                    return;
                }
                
                // 验证成绩范围
                if (scoreForm.score && (parseFloat(scoreForm.score) < 0 || parseFloat(scoreForm.score) > 100)) {
                    alert('成绩必须在0-100之间');
                    return;
                }
                
                const scoreData = {
                    student_id: scoreForm.student_id,
                    offering_id: scoreForm.offering_id,
                    score: scoreForm.status === '已修完' ? parseFloat(scoreForm.score) : null,
                    status: scoreForm.status
                };
                
                await axios.post('/api/score/', scoreData);
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('addScoreModal'));
                modal.hide();
                
                // 如果当前选中的学生与添加的学生相同，重新加载成绩数据
                if (selectedStudentId.value === scoreForm.student_id) {
                    await loadStudentScores();
                } else {
                    // 否则，切换到新添加的学生
                    await loadStudentScores(scoreForm.student_id);
                }
                
                // 重置表单
                resetScoreForm();
                alert('成绩添加成功');
            } catch (error) {
                console.error('添加成绩失败:', error);
                alert(error.response?.data?.error || '添加成绩失败，请稍后重试');
            }
        };

        const editScore = async (scId) => {
            try {
                // 找到对应的成绩记录
                const score = scores.value.find(s => s.sc_id === scId);
                if (score) {
                    // 填充表单
                    Object.assign(scoreForm, {
                        score: score.score || '',
                        status: score.status
                    });
                    editingScoreId.value = scId;
                    
                    // 打开编辑模态框
                    const modal = new bootstrap.Modal(document.getElementById('editScoreModal'));
                    modal.show();
                }
            } catch (error) {
                console.error('获取成绩信息失败:', error);
            }
        };

        const updateScore = async () => {
            if (!editingScoreId.value) return;
            
            try {
                // 验证成绩范围
                if (scoreForm.score && (parseFloat(scoreForm.score) < 0 || parseFloat(scoreForm.score) > 100)) {
                    alert('成绩必须在0-100之间');
                    return;
                }
                
                // 如果状态是已修完，确保有成绩
                if (scoreForm.status === '已修完' && (!scoreForm.score || scoreForm.score === '')) {
                    alert('已修完状态需要填写成绩');
                    return;
                }
                
                const updateData = {
                    score: scoreForm.status === '已修完' ? parseFloat(scoreForm.score) : null,
                    status: scoreForm.status
                };
                
                await axios.put(`/api/score/${editingScoreId.value}`, updateData);
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('editScoreModal'));
                modal.hide();
                // 重新加载成绩数据
                await loadStudentScores();
                // 重置表单
                resetScoreForm();
                alert('成绩更新成功');
            } catch (error) {
                console.error('更新成绩失败:', error);
                alert(error.response?.data?.error || '更新成绩失败，请稍后重试');
            }
        };

        const confirmDeleteScore = (scId) => {
            if (confirm('确定要删除这个成绩记录吗？')) {
                deleteScore(scId);
            }
        };

        const deleteScore = async (scId) => {
            try {
                await axios.delete(`/api/score/${scId}`);
                // 重新加载成绩数据
                await loadStudentScores();
                alert('成绩记录删除成功');
            } catch (error) {
                console.error('删除成绩记录失败:', error);
                alert(error.response?.data?.error || '删除成绩记录失败，请稍后重试');
            }
        };

        // 添加openAddScoreModal函数，用于替代resetScoreForm的按钮点击事件处理
        const openAddScoreModal = () => {
            // 检查是否已选择学生
            if (!selectedStudentId.value) {
                alert('请先选择一名学生');
                return;
            }
            
            // 重置表单并预设学生ID
            Object.assign(scoreForm, {
                student_id: selectedStudentId.value,
                offering_id: '',
                score: '',
                status: '选课中'
            });
            editingScoreId.value = null;
            
            // 清空课程搜索过滤
            offeringFilter.value = '';
            
            // 打开模态框
            const modal = new bootstrap.Modal(document.getElementById('addScoreModal'));
            modal.show();
        };

        // 班级管理相关函数
        const filterClasses = () => {
            // 使用计算属性filteredClasses，无需额外处理
        };
        
        const resetClassForm = () => {
            Object.assign(classForm, {
                class_name: '',
                class_code: '',
                college_id: '',
                admission_year: new Date().getFullYear()
            });
            editingClassId.value = null;
        };
        
        const saveClass = async () => {
            try {
                await axios.post('/api/student/class', classForm);
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('addClassModal'));
                modal.hide();
                // 重新加载班级数据
                await loadClasses();
                // 重置表单
                resetClassForm();
                alert('班级添加成功');
            } catch (error) {
                console.error('添加班级失败:', error);
                alert(error.response?.data?.error || '添加班级失败，请稍后重试');
            }
        };
        
        const editClass = async (classId) => {
            try {
                const response = await axios.get(`/api/student/class/${classId}`);
                // 填充表单
                Object.assign(classForm, response.data.class);
                editingClassId.value = classId;
                
                // 打开编辑模态框
                const modal = new bootstrap.Modal(document.getElementById('editClassModal'));
                modal.show();
            } catch (error) {
                console.error('获取班级信息失败:', error);
            }
        };
        
        const updateClass = async () => {
            if (!editingClassId.value) return;
            
            try {
                await axios.put(`/api/student/class/${editingClassId.value}`, classForm);
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('editClassModal'));
                modal.hide();
                // 重新加载班级数据
                await loadClasses();
                // 重置表单
                resetClassForm();
                alert('班级更新成功');
            } catch (error) {
                console.error('更新班级失败:', error);
                alert(error.response?.data?.error || '更新班级失败，请稍后重试');
            }
        };
        
        const confirmDeleteClass = (classId) => {
            if (confirm('确定要删除这个班级吗？这可能会影响到已关联该班级的学生。')) {
                deleteClass(classId);
            }
        };
        
        const deleteClass = async (classId) => {
            try {
                await axios.delete(`/api/student/class/${classId}`);
                // 重新加载班级数据
                await loadClasses();
                alert('班级删除成功');
            } catch (error) {
                console.error('删除班级失败:', error);
                alert(error.response?.data?.error || '删除班级失败，请稍后重试');
            }
        };

        // 实时过滤班级
        watch(classSearch, debounce(() => {
            // 使用计算属性 filteredClasses 进行过滤
        }, 300));

        // 实时过滤学生
        watch(studentSearch, debounce(() => {
            studentPage.value = 1;
            if (activeModule.value === 'score') {
                loadStudents();
            }
        }, 300));

        // 实时过滤成绩
        watch(scoreFilter, debounce(() => {
            // 使用计算属性 filteredScores 进行过滤
        }, 300));

        // 在组件挂载时检查登录状态
        onMounted(() => {
            checkAuth();
        });

        // 添加表单中的过滤变量
        const classFilterForForm = ref('');
        const collegeFilterForForm = ref('');
        const titleFilterForForm = ref('');
        const courseTypeFilterForForm = ref('');
        
        // 为表单添加过滤后的计算属性
        const filteredClassesForForm = computed(() => {
            if (!classFilterForForm.value) return classes.value;
            const filter = classFilterForForm.value.toLowerCase();
            return classes.value.filter(cls => 
                cls.class_name.toLowerCase().includes(filter) || 
                cls.class_code.toLowerCase().includes(filter) ||
                cls.college_name.toLowerCase().includes(filter)
            );
        });
        
        const filteredCollegesForForm = computed(() => {
            if (!collegeFilterForForm.value) return colleges.value;
            const filter = collegeFilterForForm.value.toLowerCase();
            return colleges.value.filter(college => 
                college.college_name.toLowerCase().includes(filter) || 
                college.college_code.toLowerCase().includes(filter)
            );
        });
        
        const filteredTitlesForForm = computed(() => {
            if (!titleFilterForForm.value) return titles.value;
            const filter = titleFilterForForm.value.toLowerCase();
            return titles.value.filter(title => 
                title.title_name.toLowerCase().includes(filter) || 
                title.title_code.toLowerCase().includes(filter)
            );
        });
        
        const filteredCourseTypesForForm = computed(() => {
            if (!courseTypeFilterForForm.value) return courseTypes.value;
            const filter = courseTypeFilterForForm.value.toLowerCase();
            return courseTypes.value.filter(type => 
                type.type_name.toLowerCase().includes(filter) || 
                type.type_code.toLowerCase().includes(filter)
            );
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
            
            // 详情查看
            viewingStudent,
            viewingTeacher,
            viewingCourse,
            viewingOffering,
            
            // 过滤搜索
            courseFilter,
            teacherFilter,
            offeringFilter,
            
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
            sortedStudents,
            
            // 教师管理相关
            teachers,
            teacherTotal,
            teacherPage,
            teacherSearch,
            titles,
            teacherForm,
            searchTeachers,
            saveTeacher,
            viewTeacher,
            editTeacher,
            updateTeacher,
            confirmDeleteTeacher,
            sortedTeachers,
            
            // 课程管理相关
            courses,
            courseTotal,
            coursePage,
            courseSearch,
            courseTypes,
            courseForm,
            searchCourses,
            saveCourse,
            viewCourse,
            editCourse,
            updateCourse,
            confirmDeleteCourse,
            sortedCourses,
            
            // 授课管理相关
            offerings,
            offeringTotal,
            offeringPage,
            offeringSearch,
            offeringForm,
            searchOfferings,
            saveOffering,
            viewOffering,
            editOffering,
            updateOffering,
            confirmDeleteOffering,
            sortedOfferings,
            
            // 成绩管理相关
            scores,
            scoreTotal,
            scorePage,
            scoreSearch,
            selectedStudentId,
            selectedStudentInfo,
            scoreForm,
            editingScoreId,
            searchScores,
            loadStudentScores,
            saveScore,
            editScore,
            updateScore,
            confirmDeleteScore,
            scoreFilter,
            filteredScores,
            filterScores,
            openAddScoreModal,
            
            // 成绩统计
            totalCredits,
            averageScore,
            completedCourses,
            
            // 过滤后的列表
            filteredCourses,
            filteredTeachers,
            filteredOfferings,
            
            // 班级管理相关
            classTabActive,
            classSearch,
            collegeSearch,
            classForm,
            collegeForm,
            filteredClasses,
            sortedClasses,
            filterClasses,
            saveClass,
            editClass,
            updateClass,
            confirmDeleteClass,
            editingClassId,
            editingCollegeId,
            filteredColleges,
            sortedColleges,
            resetCollegeForm,
            saveCollege,
            editCollege,
            updateCollege,
            confirmDeleteCollege,
            deleteCollege,
            
            // 排序相关
            toggleSort,
            getSortIcon,
            studentSortField,
            studentSortOrder,
            teacherSortField,
            teacherSortOrder,
            classSortField,
            classSortOrder,
            courseSortField,
            courseSortOrder,
            offeringSortField,
            offeringSortOrder,
            
            // 表单过滤
            classFilterForForm,
            collegeFilterForForm,
            titleFilterForForm,
            courseTypeFilterForForm,
            filteredClassesForForm,
            filteredCollegesForForm,
            filteredTitlesForForm,
            filteredCourseTypesForForm
        };
    }
});

// 挂载应用
app.mount('#app');

// 用于更新学生详情模态框内容的函数
function updateStudentModalContent(student) {
    const content = document.getElementById('studentDetailContent');
    if (!content) return;
    
    content.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header">基本信息</div>
                    <div class="card-body">
                        <p><strong>学号：</strong> ${student.student_no}</p>
                        <p><strong>姓名：</strong> ${student.name}</p>
                        <p><strong>性别：</strong> ${student.gender}</p>
                        <p><strong>出生日期：</strong> ${student.birth_date || '未设置'}</p>
                        <p><strong>身份证号：</strong> ${student.id_card || '未设置'}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header">学籍信息</div>
                    <div class="card-body">
                        <p><strong>入学日期：</strong> ${student.enrollment_date}</p>
                        <p><strong>班级：</strong> ${student.class_name}</p>
                        <p><strong>学院：</strong> ${student.college_name}</p>
                        <p><strong>状态：</strong> ${student.status}</p>
                    </div>
                </div>
            </div>
            <div class="col-12">
                <div class="card">
                    <div class="card-header">联系方式</div>
                    <div class="card-body">
                        <p><strong>地址：</strong> ${student.address || '未设置'}</p>
                        <p><strong>电话：</strong> ${student.phone || '未设置'}</p>
                        <p><strong>邮箱：</strong> ${student.email || '未设置'}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 用于更新教师详情模态框内容的函数
function updateTeacherModalContent(teacher) {
    const content = document.getElementById('teacherDetailContent');
    if (!content) return;
    
    content.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header">基本信息</div>
                    <div class="card-body">
                        <p><strong>工号：</strong> ${teacher.teacher_no}</p>
                        <p><strong>姓名：</strong> ${teacher.name}</p>
                        <p><strong>性别：</strong> ${teacher.gender}</p>
                        <p><strong>出生日期：</strong> ${teacher.birth_date || '未设置'}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header">职务信息</div>
                    <div class="card-body">
                        <p><strong>职称：</strong> ${teacher.title_name || '未设置'}</p>
                        <p><strong>所属学院：</strong> ${teacher.college_name}</p>
                    </div>
                </div>
            </div>
            <div class="col-12">
                <div class="card">
                    <div class="card-header">联系方式</div>
                    <div class="card-body">
                        <p><strong>电话：</strong> ${teacher.phone || '未设置'}</p>
                        <p><strong>邮箱：</strong> ${teacher.email || '未设置'}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 用于更新课程详情模态框内容的函数
function updateCourseModalContent(course) {
    const content = document.getElementById('courseDetailContent');
    if (!content) return;
    
    content.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header">基本信息</div>
                    <div class="card-body">
                        <p><strong>课程代码：</strong> ${course.course_code}</p>
                        <p><strong>课程名称：</strong> ${course.course_name}</p>
                        <p><strong>学分：</strong> ${course.credit}</p>
                        <p><strong>学时：</strong> ${course.hours}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header">课程归属</div>
                    <div class="card-body">
                        <p><strong>课程类型：</strong> ${course.type_name}</p>
                        <p><strong>所属学院：</strong> ${course.college_name}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 用于更新授课详情模态框内容的函数
function updateOfferingModalContent(offering) {
    const content = document.getElementById('offeringDetailContent');
    if (!content) return;
    
    content.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header">课程信息</div>
                    <div class="card-body">
                        <p><strong>课程名称：</strong> ${offering.course_name}</p>
                        <p><strong>课程代码：</strong> ${offering.course_code}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header">授课教师</div>
                    <div class="card-body">
                        <p><strong>教师姓名：</strong> ${offering.teacher_name}</p>
                    </div>
                </div>
            </div>
            <div class="col-12">
                <div class="card">
                    <div class="card-header">授课安排</div>
                    <div class="card-body">
                        <p><strong>学年：</strong> ${offering.year}</p>
                        <p><strong>学期：</strong> ${offering.semester}</p>
                        <p><strong>教室：</strong> ${offering.classroom || '未指定'}</p>
                        <p><strong>上课时间：</strong> ${offering.class_time || '未指定'}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
} 