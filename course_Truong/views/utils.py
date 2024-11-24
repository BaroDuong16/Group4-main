def query_all_sub_courses(course, context:dict):
    sub_courses = course.sub_courses.all()
    for sub_course in sub_courses:
        modules = sub_course.modules.all().order_by("order")
        quizzes = sub_course.quizzes.all().order_by("order")
        
        context['sub_courses'][sub_course] = {
            'modules': {},
            'quizzes': quizzes,
        }

        for module in modules:
            sub_modules = module.sub_modules.all().order_by("order")

            context['sub_courses'][sub_course]['modules'][module] = sub_modules