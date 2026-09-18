import { useState, useEffect } from 'react';
import { Upload } from 'lucide-react';
import { Modal } from '@/components/ui/Modal';
import { Field, Select } from '@/components/ui/Form';
import { certTypes, employees } from '@/data/mockData';
import type { Employee, Certification } from '@/types';

export interface CertFormState {
  employeeId: string;
  name: string;
  issuer: string;
  issueDate: string;
  expiryDate: string;
  credentialId: string;
}

const emptyForm: CertFormState = {
  employeeId: '',
  name: '',
  issuer: '',
  issueDate: '',
  expiryDate: '',
  credentialId: '',
};

export function CertFormModal({
  open,
  onClose,
  employee,
  cert,
  mode,
}: {
  open: boolean;
  onClose: () => void;
  employee?: Employee;
  cert?: Certification;
  mode: 'create' | 'edit';
}) {
  const [form, setForm] = useState<CertFormState>(emptyForm);

  useEffect(() => {
    if (open) {
      if (cert && mode === 'edit') {
        setForm({
          employeeId: employee?.id ?? '',
          name: cert.name,
          issuer: cert.issuer,
          issueDate: cert.issueDate,
          expiryDate: cert.expiryDate,
          credentialId: cert.credentialId,
        });
      } else {
        setForm({ ...emptyForm, employeeId: employee?.id ?? '' });
      }
    }
  }, [open, employee, cert, mode]);

  const update = (k: keyof CertFormState, v: string) => setForm((f) => ({ ...f, [k]: v }));

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={mode === 'create' ? 'Agregar certificación' : 'Editar certificación'}
      description={mode === 'create' ? 'Registra una nueva certificación' : 'Actualiza los datos de la certificación'}
      size="lg"
      footer={
        <>
          <button onClick={onClose} className="btn-secondary">Cancelar</button>
          <button onClick={onClose} className="btn-primary">
            {mode === 'create' ? 'Agregar certificación' : 'Guardar cambios'}
          </button>
        </>
      }
    >
      <div className="space-y-5">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Empleado" required>
            <Select
              value={form.employeeId}
              onChange={(v) => update('employeeId', v)}
              options={employees.map((e) => `${e.firstName} ${e.lastName}`)}
              allLabel="Selecciona un empleado"
            />
          </Field>
          <Field label="Tipo de certificación" required>
            <Select
              value={form.name}
              onChange={(v) => update('name', v)}
              options={certTypes}
              allLabel="Selecciona un tipo"
            />
          </Field>
          <Field label="Entidad emisora" required>
            <input className="input-base" value={form.issuer} onChange={(e) => update('issuer', e.target.value)} placeholder="Ej. PMI, ISO, Amazon" />
          </Field>
          <Field label="ID de credencial">
            <input className="input-base" value={form.credentialId} onChange={(e) => update('credentialId', e.target.value)} placeholder="Ej. PMP-2024-001" />
          </Field>
          <Field label="Fecha de emisión" required>
            <input type="date" className="input-base" value={form.issueDate} onChange={(e) => update('issueDate', e.target.value)} />
          </Field>
          <Field label="Fecha de vencimiento" required>
            <input type="date" className="input-base" value={form.expiryDate} onChange={(e) => update('expiryDate', e.target.value)} />
          </Field>
        </div>

        <div className="rounded-xl2 border-2 border-dashed border-ink-200 px-5 py-6 text-center transition-colors hover:border-primary-300 hover:bg-primary-50/30">
          <Upload className="mx-auto h-8 w-8 text-ink-300" />
          <p className="mt-2 text-sm font-medium text-ink-700">Arrastra el documento de la certificación</p>
          <p className="text-xs text-ink-400">o haz clic para seleccionar un archivo (PDF, JPG, PNG)</p>
          <button className="btn-secondary mt-3">Seleccionar archivo</button>
        </div>
      </div>
    </Modal>
  );
}
