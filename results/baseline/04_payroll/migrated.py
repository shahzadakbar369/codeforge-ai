import math

def round_money(amount):
    return round(amount, 2)

def format_money(amount):
    return f"${amount:,.2f}"

def overtime_hours(hours, threshold=40):
    if hours <= threshold:
        return 0
    return hours - threshold

def income_tax(gross):
    if gross <= 1000:
        return 0
    tax = 0
    if gross > 6000:
        tax += (gross - 6000) * 0.30
        gross = 6000
    if gross > 3000:
        tax += (gross - 3000) * 0.20
        gross = 3000
    tax += (gross - 1000) * 0.10
    return round_money(tax)

class Employee:
    def __init__(self, name, rate, hours, is_manager=False):
        if not isinstance(name, str) or name.strip() == "":
            raise ValueError("Name is required")
        if rate < 0:
            raise ValueError("Rate cannot be negative")
        if hours < 0:
            raise ValueError("Hours cannot be negative")
        self.name = name.strip()
        self.rate = rate
        self.hours = hours
        self.is_manager = is_manager

    def regular_pay(self):
        regular_hours = min(self.hours, 40)
        return round_money(regular_hours * self.rate)

    def overtime_pay(self):
        ot = overtime_hours(self.hours)
        tier1 = min(ot, 20)
        tier2 = ot - tier1
        return round_money(tier1 * self.rate * 1.5 + tier2 * self.rate * 2)

    def bonus(self):
        if self.is_manager and self.hours >= 40:
            return round_money(self.regular_pay() * 0.10)
        return 0

    def gross_pay(self):
        return round_money(self.regular_pay() + self.overtime_pay() + self.bonus())

    def tax(self):
        return income_tax(self.gross_pay())

    def net_pay(self):
        return round_money(self.gross_pay() - self.tax())


def employee_from_array(emp):
    manager = emp.get("manager", False)
    return Employee(emp["name"], emp["rate"], emp["hours"], manager)


def employee_gross(name, rate, hours, is_manager=False):
    e = Employee(name, rate, hours, is_manager)
    return e.gross_pay()


def employee_net(name, rate, hours, is_manager=False):
    e = Employee(name, rate, hours, is_manager)
    return e.net_pay()


def employee_payslip(name, rate, hours, is_manager=False):
    e = Employee(name, rate, hours, is_manager)
    return {
        "name": e.name,
        "regular": e.regular_pay(),
        "overtime": e.overtime_pay(),
        "bonus": e.bonus(),
        "gross": e.gross_pay(),
        "tax": e.tax(),
        "net": e.net_pay(),
    }


def payslip_line(name, rate, hours, is_manager=False):
    slip = employee_payslip(name, rate, hours, is_manager)
    return f"{slip['name']}: {format_money(slip['net'])}"


def payroll_total(employees):
    total = 0
    for emp in employees:
        e = employee_from_array(emp)
        total += e.net_pay()
    return round_money(total)


def highest_paid(employees):
    if len(employees) == 0:
        raise ValueError("No employees")
    best = None
    best_gross = -1
    for emp in employees:
        e = employee_from_array(emp)
        gross = e.gross_pay()
        if gross > best_gross:
            best_gross = gross
            best = e.name
    return best


def department_summary(employees):
    count = len(employees)
    gross = 0
    net = 0
    for emp in employees:
        e = employee_from_array(emp)
        gross += e.gross_pay()
        net += e.net_pay()
    average = round_money(net / count) if count > 0 else 0
    return {
        "count": count,
        "total_gross": round_money(gross),
        "total_net": round_money(net),
        "average_net": average,
    }
