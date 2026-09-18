import { useState, useEffect } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Field, Select } from '@/components/ui/Form';
import { departments, positions } from '@/data/mockData';
import type { Employee } from '@/types';

export interface EmployeeFormState {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  position: string;
  department: string;
  status: string;
  hireDate: string;
  location: string;
}

const emptyForm: EmployeeFormState = {
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  position: '',
  department: '',
  status: 'active',
  hireDate: '',
  location: '',
};

const statusOptions = [
  { value: 'active', label: 'Activo' },
  { value: 'on_leave', label: 'De licencia' },
  { value: 'inactive', label: 'Inactivo' },
];

export function EmployeeFormModal({
  open,
  onClose,
  employee,
  mode,
}: {
  open: boolean;
  onClose: () => void;
  employee?: Employee;
  mode: 'create' | 'edit';
}) {
  const [form, setForm] = useState<EmployeeFormState>(emptyForm);

  useEffect(() => {
    if (open) {
      if (employee && mode === 'edit') {
        setForm({
          firstName: employee.firstName,
          lastName: employee.lastName,
          email: employee.email,
          phone: employee.phone,
          position: employee.position,
          department: employee.department,
          status: employee.status,
          hireDate: employee.hireDate,
          location: employee.location,
        });
      } else {
        setForm(emptyForm);
      }
    }
  }, [open, employee, mode]);

  const update = (k: keyof EmployeeFormState, v: string) => setForm((f) => ({ ...f, [k]: v }));

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={mode === 'create' ? 'Nuevo empleado' : 'Editar empleado'}
      description={mode === 'create' ? 'Registra un nuevo empleado en el sistema' : 'Actualiza la información del empleado'}
      size="lg"
      footer={
        <>
          <button onClick={onClose} className="btn-secondary">Cancelar</button>
          <button onClick={onClose} className="btn-primary">
            {mode === 'create' ? 'Crear empleado' : 'Guardar cambios'}
          </button>
        </>
      }
    >
      <div className="space-y-5">
        <section>
          <h3 className="mb-3 text-sm font-semibold text-ink-900">Información personal</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Field label="Nombre" required>
              <input className="input-base" value={form.firstName} onChange={(e) => update('firstName', e.target.value)} placeholder="Ej. María" />
            </Field>
            <Field label="Apellidos" required>
              <input className="input-base" value={form.lastName} onChange={(e) => update('lastName', e.target.value)} placeholder="Ej. González" />
            </Field>
            <Field label="Correo electrónico" required>
              <input type="email" className="input-base" value={form.email} onChange={(e) => update('email', e.target.value)} placeholder="nombre@empresa.com" />
            </Field>
            <Field label="Teléfono">
              <input className="input-base" value={form.phone} onChange={(e) => update('phone', e.target.value)} placeholder="+34 600 00 00 00" />
            </Field>
            <Field label="Ubicación">
              <input className="input-base" value={form.location} onChange={(e) => update('location', e.target.value)} placeholder="Madrid, ES" />
            </Field>
          </div>
        </section>

        <div className="h-px bg-ink-100" />

        <section>
          <h3 className="mb-3 text-sm font-semibold text-ink-900">Información laboral</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Field label="Cargo" required>
              <Select value={form.position} onChange={(v) => update('position', v)} options={positions} allLabel="Selecciona un cargo" />
            </Field>
            <Field label="Departamento" required>
              <Select value={form.department} onChange={(v) => update('department', v)} options={departments} allLabel="Selecciona un departamento" />
            </Field>
            <Field label="Estado" required>
              <Select
                value={form.status}
                onChange={(v) => update('status', v)}
                options={statusOptions.map((s) => s.label)}
                allLabel="Selecciona un estado"
              />
            </Field>
            <Field label="Fecha de ingreso" required>
              <input type="date" className="input-base" value={form.hireDate} onChange={(e) => update('hireDate', e.target.value)} />
            </Field>
          </div>
        </section>
      </div>
    </Modal>
  );
}
