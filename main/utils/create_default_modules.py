from module_group.models import Module, ModuleGroup


def create_default_modules():
    acc_infos = {
        "Subject" : {
            "module_url" : "subject:subject_list",
            "icon" : "fas fa-book",
            "module_group_id" : "Training Management",
        },
        "Category" : {
            "module_url" : "category:category_list",
            "icon" : "fas fa-tags",
            "module_group_id" : "Training Management",
        },
        "Training Program" : {
            "module_url" : "training_program:training_program_list",
            "icon" : "fas fa-calendar-alt",
            "module_group_id" : "Training Management",
        },

        "User" : {
            "module_url" : "user:user_list",
            "icon" : "fas fa-user",
            "module_group_id" : "User Management",
        },
        "Role" : {
            "module_url" : "role:role_list",
            "icon" : "fas fa-briefcase",
            "module_group_id" : "User Management",
        },
        "Module" : {
            "module_url" : "module_group:module_list",
            "icon" : "fas fa-cogs",
            "module_group_id" : "User Management",
        },
        "Module Group" : {
            "module_url" : "module_group:module_group_list",
            "icon" : "fas fa-folder",
            "module_group_id" : "User Management",
        },
        "User Module" : {
            "module_url" : "user_module:user_module_list",
            "icon" : "fas fa-user-tag",
            "module_group_id" : "User Management",
        },

        "Quiz" : {
            "module_url" : "question:question_list",
            "icon" : "fas fa-user-tag",
            "module_group_id" : "Assessment Management",
        },

        "Course" : {
            "module_url" : "course:course_list",
            "icon" : "fa-brands fa-leanpub",
            "module_group_id" : "Assessment Management",
        },

        "Generate Exams" : {
            "module_url" : "tools:exam_generator_view",
            "icon" : "fas fa-user-tag",
            "module_group_id" : "Tools",
        },

        "Excel to JSON" : {
            "module_url" : "tools:export_excel_to_json",
            "icon" : "fas fa-user-tag",
            "module_group_id" : "Tools",
        },

        "TXT to JSON" : {
            "module_url" : "tools:export_txt_to_json",
            "icon" : "fas fa-user-tag",
            "module_group_id" : "Tools",
        },
    }

    print("Create module!")
    for key, value in acc_infos.items():
        value['module_group_id'] = ModuleGroup.objects.get(group_name= value['module_group_id']).id
        module, created = Module.objects.get_or_create(module_name=key, defaults=value)

        if created:
            module.save()
            print(f"-- '{module}' created!")
        else:
            print(f"-- '{module}' existed!")