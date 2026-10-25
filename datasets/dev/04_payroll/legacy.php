<?php
require __DIR__ . '/helpers.php';

class Employee {
    public $name;
    public $rate;
    public $hours;
    public $is_manager;

    public function __construct($name, $rate, $hours, $is_manager = false) {
        if (trim($name) === "") {
            throw new InvalidArgumentException("Name is required");
        }
        if ($rate < 0) {
            throw new InvalidArgumentException("Rate cannot be negative");
        }
        if ($hours < 0) {
            throw new InvalidArgumentException("Hours cannot be negative");
        }
        $this->name = trim($name);
        $this->rate = $rate;
        $this->hours = $hours;
        $this->is_manager = $is_manager;
    }

    public function regular_pay() {
        $regular_hours = min($this->hours, 40);
        return round_money($regular_hours * $this->rate);
    }

    // First 20 overtime hours at 1.5x, anything beyond that at 2x.
    public function overtime_pay() {
        $ot = overtime_hours($this->hours);
        $tier1 = min($ot, 20);
        $tier2 = $ot - $tier1;
        return round_money($tier1 * $this->rate * 1.5 + $tier2 * $this->rate * 2);
    }

    // Managers who worked a full week get 10% of their regular pay.
    public function bonus() {
        if ($this->is_manager && $this->hours >= 40) {
            return round_money($this->regular_pay() * 0.10);
        }
        return 0;
    }

    public function gross_pay() {
        return round_money($this->regular_pay() + $this->overtime_pay() + $this->bonus());
    }

    public function tax() {
        return income_tax($this->gross_pay());
    }

    public function net_pay() {
        return round_money($this->gross_pay() - $this->tax());
    }
}

function employee_from_array($emp) {
    $manager = isset($emp["manager"]) ? $emp["manager"] : false;
    return new Employee($emp["name"], $emp["rate"], $emp["hours"], $manager);
}

function employee_gross($name, $rate, $hours, $is_manager = false) {
    $e = new Employee($name, $rate, $hours, $is_manager);
    return $e->gross_pay();
}

function employee_net($name, $rate, $hours, $is_manager = false) {
    $e = new Employee($name, $rate, $hours, $is_manager);
    return $e->net_pay();
}

function employee_payslip($name, $rate, $hours, $is_manager = false) {
    $e = new Employee($name, $rate, $hours, $is_manager);
    return array(
        "name" => $e->name,
        "regular" => $e->regular_pay(),
        "overtime" => $e->overtime_pay(),
        "bonus" => $e->bonus(),
        "gross" => $e->gross_pay(),
        "tax" => $e->tax(),
        "net" => $e->net_pay(),
    );
}

function payslip_line($name, $rate, $hours, $is_manager = false) {
    $slip = employee_payslip($name, $rate, $hours, $is_manager);
    return $slip["name"] . ": " . format_money($slip["net"]);
}

function payroll_total($employees) {
    $total = 0;
    foreach ($employees as $emp) {
        $e = employee_from_array($emp);
        $total += $e->net_pay();
    }
    return round_money($total);
}

function highest_paid($employees) {
    if (count($employees) == 0) {
        throw new InvalidArgumentException("No employees");
    }
    $best = null;
    $best_gross = -1;
    foreach ($employees as $emp) {
        $e = employee_from_array($emp);
        $gross = $e->gross_pay();
        if ($gross > $best_gross) {
            $best_gross = $gross;
            $best = $e->name;
        }
    }
    return $best;
}

function department_summary($employees) {
    $count = count($employees);
    $gross = 0;
    $net = 0;
    foreach ($employees as $emp) {
        $e = employee_from_array($emp);
        $gross += $e->gross_pay();
        $net += $e->net_pay();
    }
    $average = $count > 0 ? round_money($net / $count) : 0;
    return array(
        "count" => $count,
        "total_gross" => round_money($gross),
        "total_net" => round_money($net),
        "average_net" => $average,
    );
}
