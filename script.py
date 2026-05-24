# -*- coding: utf-8 -*-
from pyrevit import revit, forms, DB

# Пошук дублікатів для Specialty Equipment

doc = revit.doc
selection = revit.get_selection()

if not selection:
    forms.alert("Будь ласка, виберіть еталонний елемент.", exitscript=True)

# Беремо категорію прямо з вибраного елемента
reference_el = selection[0]
target_category = reference_el.Category

if not target_category:
    forms.alert("Вибраний елемент не має категорії.", exitscript=True)

# Отримуємо ID типу
el_type_id = reference_el.GetTypeId()

# 1. Збираємо всі елементи ТІЄЇ Ж КАТЕГОРІЇ, що і вибраний
collector = DB.FilteredElementCollector(doc) \
    .OfCategoryId(target_category.Id) \
    .WhereElementIsNotElementType() \
    .ToElements()

# 2. Фільтруємо лише той самий тип (Symbol)
same_type_instances = [i for i in collector if i.GetTypeId() == el_type_id]

duplicates = []
seen_points = []


def get_rounded_point(point):
    # Округлюємо координати (внутрішні одиниці Revit - фути)
    return (round(point.X, 4), round(point.Y, 4), round(point.Z, 4))


# 3. Шукаємо збіги по координатах
for item in same_type_instances:
    loc = item.Location
    if loc and hasattr(loc, 'Point'):
        p_tuple = get_rounded_point(loc.Point)

        if p_tuple in seen_points:
            duplicates.append(item)
        else:
            seen_points.append(p_tuple)

# 4. Виводимо результат
if duplicates:
    duplicate_ids = [x.Id for x in duplicates]
    # Автоматично виділяємо знайдені копії
    revit.get_selection().set_to(duplicate_ids)

    forms.alert("Успіх!\nЗнайдено дублікатів: {}\nВони виділені в моделі.".format(len(duplicates)))
    print("ID знайдених дублікатів:")
    for d_id in duplicate_ids:
        print(d_id)
else:
    forms.alert("Дублікатів не знайдено.\nВсі елементи цього типу знаходяться в різних точках.")