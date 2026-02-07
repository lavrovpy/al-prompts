# Output Format & Structure

## General Template

```markdown
# [DISCIPLINE] — НМТ [Year]
## Демонстраційний варіант

---

### [Section Instruction Banner]
*Bolded instruction text matching the section type*

**1.** [Question text]
[Options]

...

---

## Довідкові матеріали
[Reference materials if applicable]

---

## Відповіді

| Номер завдання | Правильна відповідь |
|----------------|---------------------|
| 1 | [Answer] |
| ... | ... |
```

## Section Instruction Banners

Each section starts with its official instruction in bold. Use the exact wording from examples:

**Single-choice (4 options):**
> *Завдання 1–N мають по чотири варіанти відповіді, з яких лише один правильний. Виберіть правильний, на Вашу думку, варіант відповіді й позначте його.*

**Single-choice (5 options):**
> *Завдання N–M мають по п'ять варіантів відповіді, з яких лише один правильний. Виберіть правильний варіант відповіді й позначте його.*

**Matching (4→5):**
> *У завданнях N–M до кожного з чотирьох фрагментів інформації, позначених цифрою, доберіть один правильний, на Вашу думку, варіант, позначений буквою.*

**Matching (3→5):**
> *У завданнях N–M до кожного з трьох рядків інформації, позначених цифрами, доберіть один правильний, на Вашу думку, варіант, позначений буквою.*

**Chronological sequencing:**
> *У завданнях N–M розташуйте події в хронологічній послідовності. Цифрі 1 має відповідати вибрана Вами перша подія, цифрі 2 – друга, цифрі 3 – третя, цифрі 4 – четверта.*

**Multi-select (3 from 7):**
> *Завдання N–M мають по сім варіантів відповідей, з яких лише три правильні. Виберіть і запишіть три цифри, що позначають правильні, на Вашу думку, відповіді.*

**Numerical answer:**
> *Розв'яжіть завдання N–M. Одержані числові відповіді запишіть у спеціально відведеному місці. Відповідь записуйте лише десятковим дробом, урахувавши положення коми.*

## Question Formatting

### Single-Choice
```
**1.** Question text here

А Option A text
Б Option B text
В Option C text
Г Option D text
```

### Matching
```
**21.** Instruction text.

| | Items | | | Options |
|---|-------|---|---|---------|
| 1 | Item text | | А | Option A text |
| 2 | Item text | | Б | Option B text |
| 3 | Item text | | В | Option C text |
| 4 | Item text | | Г | Option D text |
| | | | Д | Option E text |
```

### Chronological Sequencing
```
**25.** Установіть послідовність [topic].

А [Event A]
Б [Event B]
В [Event C]
Г [Event D]
```

### Multi-Select
```
**28.** Question text.

1 Statement 1
2 Statement 2
3 Statement 3
4 Statement 4
5 Statement 5
6 Statement 6
7 Statement 7
```

### Numerical Answer
```
**19.** Problem text.
[Description of graph/diagram if applicable]

Відповідь: _______
```

## Answer Key Formatting

### Simple answers
| Номер завдання | Правильна відповідь |
|----------------|---------------------|
| 1 | В |

### Matching answers
| 21 | 1–Б, 2–А, 3–В, 4–Д |

### Sequencing answers
| 25 | ВАГБ |

### Multi-select answers
| 28 | 1, 2, 4 |

### Numerical answers
| 19 | 38,5 |

## Visual Sources

Since AI cannot embed images, describe visual sources textually in brackets:

- Maps: `[Карта: територія Правобережної України, XVII ст., з позначенням основних міст]`
- Photos: `[Фото: будівля Верховної Ради України]`
- Graphs: `[Графік: залежність температури від часу, зростання з 12°C до 18°C]`
- Portraits: `[Портрет: історичний діяч у військовому мундирі]`
- Posters: `[Плакат: радянський агітаційний плакат часів індустріалізації]`

## Reference Materials (Math/Sciences only)

Include a "Довідкові матеріали" section with:
- Relevant formulas and identities
- Tables (squares, trigonometric values)
- Constants and conversion factors
- Geometry reference (area, volume formulas with diagrams)
