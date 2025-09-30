N = 100
M = 2 ** 15


def check_overflow(digits, operation_name=""):
    """Проверяет переполнение и обрезает до N разрядов"""
    if len(digits) > N:
        print(f"Предупреждение: переполнение в {operation_name}, результат обрезан до {N} разрядов")
        return delete_zeros(digits[:N])  # Обрезаем и удаляем возможные ведущие нули
    return digits


# удаляем ведущие нули
def delete_zeros(x):
    x = x[:]
    while len(x) > 1 and x[-1] == 0:
        x.pop()
    return x


# сравниваем по модулю
def cmp_abs(a, b):
    A = delete_zeros(a)
    B = delete_zeros(b)
    if len(A) != len(B):
        return 1 if len(A) > len(B) else -1
    for i in reversed(range(len(A))):
        if A[i] != B[i]:
            return 1 if A[i] > B[i] else -1
    return 0


def add(a, b):
    if isinstance(a, tuple):
        sign_a, digits_a = a
    else:
        sign_a, digits_a = 1, a

    if isinstance(b, tuple):
        sign_b, digits_b = b
    else:
        sign_b, digits_b = 1, b

    # Разные знаки - вычитаем
    if sign_a != sign_b:
        cmp_val = cmp_abs(digits_a, digits_b)
        if cmp_val == 0:
            return (1, [0])  # a + (-a) = 0

        if cmp_val > 0:
            # |a| > |b|, результат имеет знак a
            result_digits = _sub_abs(digits_a, digits_b)
            result_digits = check_overflow(result_digits, "add (substract case)")
            return (sign_a, delete_zeros(result_digits))
        else:
            # |a| < |b|, результат имеет знак b
            result_digits = _sub_abs(digits_b, digits_a)
            result_digits = check_overflow(result_digits, "add (substract case)")
            return (sign_b, delete_zeros(result_digits))

    # Одинаковые знаки - складываем модули
    result_digits = _add_abs(digits_a, digits_b)
    result_digits = check_overflow(result_digits, "add")
    return (sign_a, delete_zeros(result_digits))


def sub(a, b):
    # a - b = a + (-b)
    if isinstance(b, tuple):
        sign_b, digits_b = b
        neg_b = (-sign_b, digits_b)
    else:
        neg_b = (-1, b)

    return add(a, neg_b)


def mult(a, b):
    # Извлекаем знаки и цифры
    if isinstance(a, tuple):
        sign_a, digits_a = a
    else:
        sign_a, digits_a = 1, a

    if isinstance(b, tuple):
        sign_b, digits_b = b
    else:
        sign_b, digits_b = 1, b

    # Определяем знак результата
    result_sign = 1 if sign_a == sign_b else -1

    # Умножение модулей
    result_digits = _mult_abs(digits_a, digits_b)
    result_digits = check_overflow(result_digits, "mult")
    return (result_sign, delete_zeros(result_digits))


def div(a, b):
    if isinstance(a, tuple):
        sign_a, digits_a = a
    else:
        sign_a, digits_a = 1, a

    if isinstance(b, tuple):
        sign_b, digits_b = b
    else:
        sign_b, digits_b = 1, b

    if digits_b == [0]:
        raise ZeroDivisionError("деление на ноль")

    abs_cmp = cmp_abs(digits_a, digits_b)

    if abs_cmp < 0:
        quotient_digits = [0]
        remainder_digits = digits_a
    elif abs_cmp == 0:
        quotient_digits = [1]
        remainder_digits = [0]
    else:
        quotient_digits, remainder_digits = _div_improved(digits_a, digits_b)

    quotient_digits = check_overflow(quotient_digits, "div (quotient)")
    remainder_digits = check_overflow(remainder_digits, "div (remainder)")

    quotient_sign = 1 if sign_a == sign_b else -1

    if sign_a == -1 and remainder_digits != [0]:
        quotient_digits = _add_abs(quotient_digits, [1])
        quotient_digits = check_overflow(quotient_digits, "div (negative correction)")
        remainder_digits = _sub_abs(digits_b, remainder_digits)
        remainder_digits = check_overflow(remainder_digits, "div (negative correction)")

    quotient = (quotient_sign, delete_zeros(quotient_digits))
    remainder = (1, delete_zeros(remainder_digits))

    return quotient, remainder


def _div_improved(a, b):
    A = delete_zeros(a)
    B = delete_zeros(b)

    # Случай, когда делитель одноразрядный
    if len(B) == 1:
        return _div_single_digit(A, B[0])

    # Нормализация
    norm_factor = M // (B[-1] + 1)

    if norm_factor > 1:
        A_norm = _mult_single(A, norm_factor)
        B_norm = _mult_single(B, norm_factor)
        A_norm = delete_zeros(A_norm)
        B_norm = delete_zeros(B_norm)
    else:
        A_norm = A[:]
        B_norm = B[:]

    quotient = [0] * len(A_norm)
    remainder = A_norm[:]

    n = len(B_norm)
    m = len(A_norm) - n

    for i in range(m, -1, -1):

        if i + n < len(remainder):
            high_rem = remainder[i + n] * M + remainder[i + n - 1]
        else:
            high_rem = remainder[-1] if remainder else 0

        high_div = B_norm[-1]

        q_est = min(high_rem // high_div, M - 1)

        while True:

            temp = _mult_single(B_norm, q_est)

            # Сдвигаем результат
            temp_shifted = [0] * i + temp
            while len(temp_shifted) < len(remainder):
                temp_shifted.append(0)

            if cmp_abs(temp_shifted, remainder) <= 0:
                break
            q_est -= 1
            if q_est < 0:
                q_est = 0
                break

        # Вычитаем сдвинутый результат из остатка
        if q_est > 0:
            temp = _mult_single(B_norm, q_est)
            temp_shifted = [0] * i + temp
            while len(temp_shifted) < len(remainder):
                temp_shifted.append(0)

            remainder = _sub_abs(remainder, temp_shifted)
            remainder = delete_zeros(remainder)

        quotient[i] = q_est

    quotient = delete_zeros(quotient)

    if norm_factor > 1:
        remainder = _div_single_digit(remainder, norm_factor)[0]

    return quotient, remainder

    return result * sign


def _div_single_digit(a, divisor):
    if divisor == 0:
        raise ZeroDivisionError("деление на ноль")

    result = []
    remainder = 0

    for i in range(len(a) - 1, -1, -1):
        current = remainder * M + a[i]
        result_digit = current // divisor
        remainder = current % divisor
        result.append(result_digit)

    result.reverse()
    result = check_overflow(result, "_div_single_digit")
    return (delete_zeros(result), [remainder])


def _mult_single(a, x):
    if x == 0:
        return [0]

    result = []
    carry = 0

    for digit in a:
        product = digit * x + carry
        result.append(product % M)
        carry = product // M

    if carry:
        result.append(carry)

    return result


def _add_abs(a, b):
    result = []
    carry = 0
    max_len = max(len(a), len(b))

    for i in range(max_len):
        da = a[i] if i < len(a) else 0
        db = b[i] if i < len(b) else 0
        s = da + db + carry
        result.append(s % M)
        carry = s // M
    if carry:
        result.append(carry)

    if len(result) > N:
        print("Переполнение: результат длиннее, чем N разрядов")

    return result


def _sub_abs(a, b):
    result = []
    borrow = 0

    for i in range(len(a)):
        da = a[i]
        db = b[i] if i < len(b) else 0
        t = da - db - borrow
        if t < 0:
            t += M
            borrow = 1
        else:
            borrow = 0
        result.append(t)

    return result


def _mult_abs(a, b):
    A = delete_zeros(a)
    B = delete_zeros(b)

    if A == [0] or B == [0]:
        return [0]

    result = [0] * (len(A) + len(B))

    if len(A) < len(B):
        A, B = B, A

    for i in range(len(A)):
        carry = 0
        for j in range(len(B)):
            k = i + j
            product = A[i] * B[j] + result[k] + carry
            result[k] = product % M
            carry = product // M

        if carry > 0:
            k = i + len(B)
            while carry > 0 and k < len(result):
                total = result[k] + carry
                result[k] = total % M
                carry = total // M
                k += 1
            if carry > 0:
                result.append(carry)

    if len(result) > N:
        print("Предупреждение: возможное переполнение")

    return result


def to_str(num):
    if isinstance(num, tuple):
        sign, digits = num
        sign_str = "-" if sign == -1 else ""
        return sign_str + str(digits)
    else:
        return str(num)


def from_string(s):
    s = s.strip()

    if s.startswith('-'):
        sign = -1
        digits_str = s[1:].strip()
    else:
        sign = 1
        digits_str = s.strip()

    if digits_str.startswith('[') and digits_str.endswith(']'):
        digits_str = digits_str[1:-1]

    try:
        digits = [int(x.strip()) for x in digits_str.split(',') if x.strip()]
        return (sign, digits)
    except ValueError:
        raise ValueError(f"Неверный формат числа: {s}")


def input_number(prompt):
    while True:
        try:
            s = input(prompt)
            if s.lower() == 'exit':
                return None
            return from_string(s)
        except ValueError as e:
            print(f"Ошибка: {e}")
            print("Пожалуйста, введите число в формате: '[1, 2, 3]' или '- [1, 2, 3]'")
            print("Или введите 'exit' для выхода")


def show_menu():
    print("\n" + "=" * 50)
    print("Доступные операции:")
    print("1. Сложение")
    print("2. Вычитание")
    print("3. Умножение")
    print("4. Деление")
    print("5. Выход")
    print("=" * 50)


def main():
    print("Основание системы счисления: 2^15 =", M)
    print("Максимальная разрядность: ", N)

    while True:
        show_menu()

        choice = input("\nВыберите операцию (1-5): ").strip()

        if choice == '5' or choice.lower() == 'exit':
            print("До свидания!")
            break

        if choice not in ['1', '2', '3', '4']:
            print("Неверный выбор. Пожалуйста, выберите от 1 до 5.")
            continue

        # Ввод чисел
        print("\nВведите первое число в М-ичной системе счисления:")
        a = input_number("a = ")
        if a is None:
            break

        print("Введите второе число в М-ичной системе счисления:")
        b = input_number("b = ")
        if b is None:
            break

        # Выполнение операции
        try:
            if choice == '1':
                result = add(a, b)
                sign, digits = result

                resAdd = 0
                terms = []

                for position, digit in enumerate(digits):
                    power = (2 ** 15) ** position
                    resAdd += digit * power
                    terms.append(f"{digit}")

                sign_str = "-" if sign == -1 else ""
                print(f"\nРезультат: {to_str(a)} + {to_str(b)} = {sign_str}({' + '.join(terms)})")
                final_result = resAdd * sign
                print(f"Итоговый результат в 10-чной системе счисления: {final_result}")

            elif choice == '2':
                result = sub(a, b)
                sign, digits = result

                resSubTen = 0
                terms = []
                for position, digit in enumerate(digits):
                    power = (2 ** 15) ** position
                    resSubTen += digit * power
                    terms.append(f"{digit}")

                sign_str = "-" if sign == -1 else ""
                print(f"\nРезультат: {to_str(a)} - {to_str(b)} = {sign_str}({' + '.join(terms)})")
                final_result = resSubTen * sign
                print(f"Итоговый результат в 10-чной системе счисления: {final_result}")

            elif choice == '3':
                result = mult(a, b)
                sign, digits = result

                resMult = 0
                terms = []

                for position, digit in enumerate(digits):
                    power = (2 ** 15) ** position
                    resMult += digit * power
                    terms.append(f"{digit}")

                sign_str = "-" if sign == -1 else ""
                print(f"\nРезультат: {to_str(a)} * {to_str(b)} = {sign_str}({' + '.join(terms)})")
                final_result = resMult * sign
                print(f"Итоговый результат в 10-чной системе счисления: {final_result}")

            elif choice == '4':
                quotient, remainder = div(a, b)
                sign, digits = quotient

                resDiv = 0
                terms = []

                resDiv = 0
                for position, digit in enumerate(quotient[1]):  # quotient[1] = les chiffres
                    power = (2 ** 15) ** position
                    resDiv += digit * power
                resDiv *= quotient[0]  # Appliquer le signe

                print(f"\nРезультат деления:")
                print(f"  Частное: {to_str(resDiv)}")
                print(f"  Остаток: {to_str(remainder)}")

        except ZeroDivisionError as e:
            print(f"\nОшибка: {e}")
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")

        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()