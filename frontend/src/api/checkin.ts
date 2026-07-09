import axios, { isAxiosError } from 'axios';

export type CheckinResultado = 'exitoso' | 'denegado';

export type RazonDenegacion =
  | 'MEMBRESIA_VENCIDA'
  | 'SIN_VISITAS'
  | 'CEDULA_NO_ENCONTRADA'
  | 'DISPOSITIVO_BLOQUEADO';

export interface CheckinResponse {
  resultado: CheckinResultado;
  mensaje: string;
  nombre: string | null;
  visitas_restantes: number | null;
  razon: RazonDenegacion | null;
}

export class DispositivoBloqueadoError extends Error {
  bloqueadoHasta: Date | null;

  constructor(mensaje: string, bloqueadoHasta: Date | null) {
    super(mensaje);
    this.bloqueadoHasta = bloqueadoHasta;
  }
}

const DEVICE_ID_KEY = 'gymflow-kiosko-device-id';

// Id estable del kiosko (RN-03, 002-acceso-denegado) — persistido en
// localStorage para que sobreviva a recargas de página.
function getDeviceId(): string {
  let deviceId = localStorage.getItem(DEVICE_ID_KEY);
  if (!deviceId) {
    deviceId = crypto.randomUUID();
    localStorage.setItem(DEVICE_ID_KEY, deviceId);
  }
  return deviceId;
}

const apiClient = axios.create({ baseURL: '/api' });

export async function postCheckin(cedula: string): Promise<CheckinResponse> {
  try {
    const { data } = await apiClient.post<CheckinResponse>(
      '/checkin',
      { cedula },
      { headers: { 'X-Device-Id': getDeviceId() } },
    );
    return data;
  } catch (error) {
    if (isAxiosError(error) && error.response?.status === 423) {
      const detail = error.response.data?.detail as
        | { mensaje?: string; bloqueado_hasta?: string }
        | undefined;
      throw new DispositivoBloqueadoError(
        detail?.mensaje ?? 'Dispositivo bloqueado temporalmente.',
        detail?.bloqueado_hasta ? new Date(detail.bloqueado_hasta) : null,
      );
    }
    throw error;
  }
}
