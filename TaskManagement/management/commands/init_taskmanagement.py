"""
初始化任务管理子系统的菜单、角色和权限
运行方式: python manage.py init_taskmanagement
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from system.models import Menu, Role
from app01.models import User


class Command(BaseCommand):
    help = '初始化TaskManagement子系统的菜单、角色和权限'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化 TaskManagement 子系统...')

        # ============================================================
        # 1. 创建菜单
        # ============================================================
        self.stdout.write('创建菜单...')

        # 父级菜单：任务管理
        task_parent, _ = Menu.objects.update_or_create(
            permission='TaskManagement:menu',
            defaults={
                'name': '任务管理',
                'menu_type': Menu.MenuType.DIRECTORY,
                'path': '/task',
                'component': '',
                'icon': 'List',
                'sort': 50,
                'is_visible': True,
                'status': True,
            }
        )

        # 子菜单：任务列表
        task_list, _ = Menu.objects.update_or_create(
            permission='TaskManagement:task_list',
            defaults={
                'name': '任务列表',
                'parent': task_parent,
                'menu_type': Menu.MenuType.MENU,
                'path': '/task/index',
                'component': 'task/index',
                'icon': 'Document',
                'sort': 1,
                'is_visible': True,
                'status': True,
            }
        )

        # 子菜单：任务统计
        task_stats, _ = Menu.objects.update_or_create(
            permission='TaskManagement:task_stats',
            defaults={
                'name': '任务统计',
                'parent': task_parent,
                'menu_type': Menu.MenuType.MENU,
                'path': '/task/dashboard',
                'component': 'task/dashboard',
                'icon': 'DataAnalysis',
                'sort': 2,
                'is_visible': True,
                'status': True,
            }
        )

        # 子菜单：任务种类（管理员可见）
        task_category, _ = Menu.objects.update_or_create(
            permission='TaskManagement:category',
            defaults={
                'name': '任务种类',
                'parent': task_parent,
                'menu_type': Menu.MenuType.MENU,
                'path': '/task/category',
                'component': 'task/category',
                'icon': 'Setting',
                'sort': 3,
                'is_visible': True,
                'status': True,
            }
        )

        # 按钮权限：新增
        btn_add, _ = Menu.objects.update_or_create(
            permission='TaskManagement:task_add',
            defaults={
                'name': '新增任务',
                'parent': task_list,
                'menu_type': Menu.MenuType.BUTTON,
                'path': '',
                'component': '',
                'sort': 1,
                'is_visible': False,
                'status': True,
            }
        )

        # 按钮权限：编辑
        btn_edit, _ = Menu.objects.update_or_create(
            permission='TaskManagement:task_edit',
            defaults={
                'name': '编辑任务',
                'parent': task_list,
                'menu_type': Menu.MenuType.BUTTON,
                'path': '',
                'component': '',
                'sort': 2,
                'is_visible': False,
                'status': True,
            }
        )

        # 按钮权限：删除
        btn_delete, _ = Menu.objects.update_or_create(
            permission='TaskManagement:task_delete',
            defaults={
                'name': '删除任务',
                'parent': task_list,
                'menu_type': Menu.MenuType.BUTTON,
                'path': '',
                'component': '',
                'sort': 3,
                'is_visible': False,
                'status': True,
            }
        )

        # 按钮权限：批量删除
        btn_batch_delete, _ = Menu.objects.update_or_create(
            permission='TaskManagement:task_batch_delete',
            defaults={
                'name': '批量删除任务',
                'parent': task_list,
                'menu_type': Menu.MenuType.BUTTON,
                'path': '',
                'component': '',
                'sort': 4,
                'is_visible': False,
                'status': True,
            }
        )

        # 按钮权限：导入
        btn_import, _ = Menu.objects.update_or_create(
            permission='TaskManagement:task_import',
            defaults={
                'name': '导入任务',
                'parent': task_list,
                'menu_type': Menu.MenuType.BUTTON,
                'path': '',
                'component': '',
                'sort': 5,
                'is_visible': False,
                'status': True,
            }
        )

        # 按钮权限：导出
        btn_export, _ = Menu.objects.update_or_create(
            permission='TaskManagement:task_export',
            defaults={
                'name': '导出任务',
                'parent': task_list,
                'menu_type': Menu.MenuType.BUTTON,
                'path': '',
                'component': '',
                'sort': 6,
                'is_visible': False,
                'status': True,
            }
        )

        # 按钮权限：审批
        btn_approve, _ = Menu.objects.update_or_create(
            permission='TaskManagement:task_approve',
            defaults={
                'name': '审批任务',
                'parent': task_list,
                'menu_type': Menu.MenuType.BUTTON,
                'path': '',
                'component': '',
                'sort': 7,
                'is_visible': False,
                'status': True,
            }
        )

        self.stdout.write(self.style.SUCCESS('  菜单创建完成'))

        # ============================================================
        # 2. 创建角色
        # ============================================================
        self.stdout.write('创建角色...')

        all_menus = [task_parent, task_list, task_stats, task_category,
                     btn_add, btn_edit, btn_delete, btn_batch_delete,
                     btn_import, btn_export, btn_approve]

        # 主管/经理
        role_qm, created = Role.objects.update_or_create(
            code='DQA_QM',
            defaults={
                'name': 'DQA主管/经理',
                'remark': '任务管理系统主管角色，可查看所有员工任务，审批，签核，评分',
                'status': True,
            }
        )
        role_qm.menus.set(all_menus)
        if created:
            self.stdout.write(f'  创建角色: {role_qm.name}')

        # 主管/组长
        role_pl, created = Role.objects.update_or_create(
            code='DQA_PL',
            defaults={
                'name': 'DQA主管/组长',
                'remark': '任务管理系统组长角色，可查看所有员工任务，审批，签核，评分',
                'status': True,
            }
        )
        role_pl.menus.set(all_menus)
        if created:
            self.stdout.write(f'  创建角色: {role_pl.name}')

        # 员工
        role_te, created = Role.objects.update_or_create(
            code='DQA_TE',
            defaults={
                'name': 'DQA员工',
                'remark': '任务管理系统员工角色，只能查看自己相关任务，创建和提交审核',
                'status': True,
            }
        )
        # 员工只能看到任务列表和统计，不能看到任务种类管理
        te_menus = [task_parent, task_list, task_stats]
        role_te.menus.set(te_menus)
        if created:
            self.stdout.write(f'  创建角色: {role_te.name}')

        # 子系统管理员
        role_admin, created = Role.objects.update_or_create(
            code='DQA_C38_TaskManagement_admin',
            defaults={
                'name': '任务管理子系统管理员',
                'remark': '任务管理系统管理员，可查看编辑所有任务，进行数据维护',
                'status': True,
            }
        )
        role_admin.menus.set(all_menus)
        if created:
            self.stdout.write(f'  创建角色: {role_admin.name}')

        # 子系统使用者
        role_user, created = Role.objects.update_or_create(
            code='DQA_C38_TaskManagement_users',
            defaults={
                'name': '任务管理子系统使用者',
                'remark': '任务管理系统普通使用者',
                'status': True,
            }
        )
        role_user.menus.set(te_menus)
        if created:
            self.stdout.write(f'  创建角色: {role_user.name}')

        self.stdout.write(self.style.SUCCESS('  角色创建完成'))

        # ============================================================
        # 3. 创建 Django 权限（用于 admin 和按钮权限）
        # ============================================================
        self.stdout.write('创建 Django 权限...')
        from TaskManagement.models import TaskCategory, Task, TaskApproval, TaskProgressRecord, TaskPerformance

        models = [TaskCategory, Task, TaskApproval, TaskProgressRecord, TaskPerformance]
        for model in models:
            ct = ContentType.objects.get_for_model(model)
            Permission.objects.get_or_create(
                codename=f'view_{model._meta.model_name}',
                content_type=ct,
                defaults={'name': f'Can view {model._meta.verbose_name}'}
            )
            Permission.objects.get_or_create(
                codename=f'add_{model._meta.model_name}',
                content_type=ct,
                defaults={'name': f'Can add {model._meta.verbose_name}'}
            )
            Permission.objects.get_or_create(
                codename=f'change_{model._meta.model_name}',
                content_type=ct,
                defaults={'name': f'Can change {model._meta.verbose_name}'}
            )
            Permission.objects.get_or_create(
                codename=f'delete_{model._meta.model_name}',
                content_type=ct,
                defaults={'name': f'Can delete {model._meta.verbose_name}'}
            )

        self.stdout.write(self.style.SUCCESS('  Django权限创建完成'))

        # ============================================================
        # 完成
        # ============================================================
        self.stdout.write(self.style.SUCCESS('\nTaskManagement 子系统初始化完成！'))
        self.stdout.write('\n角色列表：')
        self.stdout.write('  - DQA_QM: 主管/经理（查看所有任务，审批，签核，评分）')
        self.stdout.write('  - DQA_PL: 主管/组长（查看所有任务，审批，签核，评分）')
        self.stdout.write('  - DQA_TE: 员工（只看自己相关任务，创建和提交审核）')
        self.stdout.write('  - DQA_C38_TaskManagement_admin: 子系统管理员（查看编辑所有任务）')
        self.stdout.write('  - DQA_C38_TaskManagement_users: 子系统使用者')
        self.stdout.write('\n菜单位置：任务管理 > 任务列表 / 任务统计 / 任务种类')
        self.stdout.write('\n请使用以下命令添加默认任务种类：')
        self.stdout.write('  python manage.py shell -c "from TaskManagement.models import TaskCategory; cats = [{\'name\':\'日常任务\',\'code\':\'daily\',\'has_benefit\':False,\'sort\':1},{\'name\':\'项目任务\',\'code\':\'project\',\'has_benefit\':True,\'sort\':2},{\'name\':\'改善任务\',\'code\':\'improvement\',\'has_benefit\':True,\'sort\':3},{\'name\':\'培训任务\',\'code\':\'training\',\'has_benefit\':False,\'sort\':4},{\'name\':\'审核任务\',\'code\':\'audit\',\'has_benefit\':False,\'sort\':5}]; [TaskCategory.objects.get_or_create(**c) for c in cats]; print(\'默认任务种类创建完成\')"')