import { isAxiosError } from 'axios';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, type FormEvent } from 'react';

import {
  createMembershipType,
  deleteMembershipType,
  listMembershipTypesAdmin,
  updateMembershipType,
  type MembershipTypeAdmin,
  type MembershipTypeCreate,
} from '../../api/members';
import { useAuth } from '../../context/useAuth';

const QUERY_KEY = ['tipos-membresia-admin'];

const FORM_INICIAL: MembershipTypeCreate = {
  nombre: '',
  precio_base: '',
  visitas_totales: 0,
  cupo_invitados: 0,
  duracion_dias: 30,
  activo: true,
};

function mensajeError(error: unknown, fallback: string): string {
  if (isAxiosError(error) && error.response?.status === 409) {
    const detail = error.response.data?.detail;
    return typeof detail === 'string' ? detail : fallback;
  }
  return fallback;
}

function MembershipTypesPage() {
  const auth = useAuth();
  const queryClient = useQueryClient();
  const esAdmin = auth.rol === 'administrador';

  const tipos = useQuery({
    queryKey: QUERY_KEY,
    queryFn: listMembershipTypesAdmin,
    enabled: esAdmin,
  });

  const [form, setForm] = useState<MembershipTypeCreate>(FORM_INICIAL);

  const crear = useMutation({
    mutationFn: () => createMembershipType(form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      setForm(FORM_INICIAL);
    },
  });

  const alternarActivo = useMutation({
    mutationFn: (tipo: MembershipTypeAdmin) =>
      updateMembershipType(tipo.id, { activo: !tipo.activo }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: QUERY_KEY }),
  });

  const eliminar = useMutation({
    mutationFn: (tipoId: number) => deleteMembershipType(tipoId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: QUERY_KEY }),
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (crear.isPending) return;
    crear.mutate();
  }

  if (!esAdmin) {
    return (
      <div>
        <h1 className="text-member-navy-text text-2xl font-semibold mb-4">Tipos de membresía</h1>
        <p className="text-red-600 bg-red-50 border border-red-200 rounded p-3">
          Solo un Administrador puede configurar los tipos de membresía.
        </p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-member-navy-text text-2xl font-semibold mb-4">Tipos de membresía</h1>

      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-card shadow border border-gray-200 p-4 mb-6 flex flex-wrap items-end gap-3"
      >
        <div>
          <label className="block text-xs text-gray-600 mb-1" htmlFor="nombre">Nombre</label>
          <input
            id="nombre" required value={form.nombre}
            onChange={(e) => setForm({ ...form, nombre: e.target.value })}
            className="w-40 border border-gray-300 rounded px-2 py-1 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-600 mb-1" htmlFor="precio">Precio base</label>
          <input
            id="precio" required inputMode="decimal" value={form.precio_base}
            onChange={(e) => setForm({ ...form, precio_base: e.target.value })}
            className="w-28 border border-gray-300 rounded px-2 py-1 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-600 mb-1" htmlFor="visitas">Visitas</label>
          <input
            id="visitas" type="number" min={0} required value={form.visitas_totales}
            onChange={(e) => setForm({ ...form, visitas_totales: Number(e.target.value) })}
            className="w-20 border border-gray-300 rounded px-2 py-1 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-600 mb-1" htmlFor="cupo">Cupo invitados</label>
          <input
            id="cupo" type="number" min={0} required value={form.cupo_invitados}
            onChange={(e) => setForm({ ...form, cupo_invitados: Number(e.target.value) })}
            className="w-24 border border-gray-300 rounded px-2 py-1 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-600 mb-1" htmlFor="duracion">Duración (días)</label>
          <input
            id="duracion" type="number" min={1} required value={form.duracion_dias}
            onChange={(e) => setForm({ ...form, duracion_dias: Number(e.target.value) })}
            className="w-24 border border-gray-300 rounded px-2 py-1 text-sm"
          />
        </div>
        <button
          type="submit" disabled={crear.isPending}
          className="bg-member-navy text-white rounded px-3 py-1.5 text-sm disabled:opacity-50"
        >
          Crear tipo
        </button>
      </form>

      {crear.isError && (
        <p className="text-red-600 text-sm mb-4">No se pudo crear el tipo de membresía.</p>
      )}
      {alternarActivo.isError && (
        <p className="text-red-600 text-sm mb-4">
          {mensajeError(alternarActivo.error, 'No se pudo cambiar el estado del tipo.')}
        </p>
      )}
      {eliminar.isError && (
        <p className="text-red-600 text-sm mb-4">
          {mensajeError(eliminar.error, 'No se pudo eliminar el tipo.')}
        </p>
      )}

      {tipos.isLoading && <p className="text-gray-500">Cargando…</p>}

      {tipos.data && (
        <table className="w-full bg-white rounded-card shadow border border-gray-200 text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b border-gray-200">
              <th className="p-3">Nombre</th>
              <th className="p-3">Precio base</th>
              <th className="p-3">Visitas</th>
              <th className="p-3">Cupo invitados</th>
              <th className="p-3">Duración</th>
              <th className="p-3">Estado</th>
              <th className="p-3" />
            </tr>
          </thead>
          <tbody>
            {tipos.data.map((t) => (
              <tr key={t.id} className="border-b border-gray-100 last:border-0">
                <td className="p-3 text-gray-900">{t.nombre}</td>
                <td className="p-3 text-gray-900">{t.precio_base}</td>
                <td className="p-3 text-gray-900">{t.visitas_totales}</td>
                <td className="p-3 text-gray-900">{t.cupo_invitados}</td>
                <td className="p-3 text-gray-900">{t.duracion_dias} días</td>
                <td className="p-3">
                  <span
                    className={
                      t.activo
                        ? 'text-green-700 bg-green-50 border border-green-200 rounded px-2 py-0.5 text-xs'
                        : 'text-gray-500 bg-gray-50 border border-gray-200 rounded px-2 py-0.5 text-xs'
                    }
                  >
                    {t.activo ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td className="p-3 text-right whitespace-nowrap">
                  <button
                    onClick={() => alternarActivo.mutate(t)}
                    className="text-sm text-member-navy border border-gray-300 rounded px-2 py-1 hover:bg-gray-50 mr-2"
                  >
                    {t.activo ? 'Desactivar' : 'Activar'}
                  </button>
                  <button
                    onClick={() => eliminar.mutate(t.id)}
                    className="text-sm text-red-600 border border-red-200 rounded px-2 py-1 hover:bg-red-50"
                  >
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default MembershipTypesPage;
