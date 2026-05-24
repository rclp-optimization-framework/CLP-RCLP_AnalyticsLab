% -----------------------------
% PARÁMETROS DEL PROBLEMA
% -----------------------------

int: num_buses;                 % número total de buses
set of int: b = 1..num_buses;   % conjunto de buses

int: num_stations;              % número total de estaciones posibles
set of int: st = 1..num_stations;

int: max_stops;                 % máximo número de paradas por bus
array[b] of int: num_stops;     % número real de paradas por bus

% mapeo de cada parada del bus a una estación física
array[b,1..max_stops] of int: st_bi;

% -----------------------------
% ESCALA NUMÉRICA
% -----------------------------

int: scale = 10;                % factor de escala para trabajar con enteros

% -----------------------------
% CONSTANTES DEL MODELO
% -----------------------------

int: consumo_max;   % capacidad máxima de la batería
int: consumo_min;   % nivel mínimo permitido de batería
int: alpha;         % tasa de carga energética (energía por unidad de tiempo)
int: mu;            % desviación máxima permitida respecto al horario
int: sm;            % margen de seguridad entre eventos de carga
int: psi;           % tiempo mínimo de carga
int: beta;          % tiempo máximo de carga
int: m;             % constante grande para restricciones lógicas (big-m)

% -----------------------------
% DATOS DE LAS RUTAS
% -----------------------------

array[b,1..max_stops] of int: d;      % energía consumida entre paradas
array[b,1..max_stops] of int: t;      % tiempo de viaje entre paradas
array[b,1..max_stops] of int: tau_bi; % horario planificado de llegada

% -----------------------------
% VARIABLES DE DECISIÓN
% -----------------------------

array[b,1..max_stops] of var 0..1600: cbi;   % nivel de batería al llegar
array[b,1..max_stops] of var 0..1600: ebi;   % energía cargada en la parada
array[b,1..max_stops] of var 0..600: ctbi;   % tiempo dedicado a cargar
array[b,1..max_stops] of var 0..3000: tbi;   % tiempo real de llegada
array[b,1..max_stops] of var 0..500: d_tbi;  % desviación respecto al horario

array[b,1..max_stops] of var 0..1: xbi;      % 1 si el bus carga en la parada

array[st] of var 0..1: xst;                  % 1 si se instala estación

% variables auxiliares para evitar solapamientos de carga
array[b,b,1..max_stops,1..max_stops] of var 0..1: zbdij;
array[b,b,1..max_stops,1..max_stops] of var 0..1: zbdi;

% -----------------------------
% A. CAPACIDAD DE BATERÍA
% -----------------------------

constraint forall(bus in b) (
    cbi[bus,1] = consumo_max
);

constraint forall(bus in b, i in 1..num_stops[bus]) (
    cbi[bus,i] >= consumo_min /\
    cbi[bus,i] + ebi[bus,i] <= consumo_max /\
    alpha * ctbi[bus,i] >= ebi[bus,i]
);

constraint forall(bus in b, i in 2..num_stops[bus]) (
    cbi[bus,i] <= cbi[bus,i-1] + ebi[bus,i-1] - d[bus,i]
);

% -----------------------------
% B. RESTRICCIONES DE TIEMPO
% -----------------------------

constraint forall(bus in b, i in 2..num_stops[bus]) (
    tbi[bus,i] >= tbi[bus,i-1] + ctbi[bus,i-1] + t[bus,i] /\
    tbi[bus,i] >= tbi[bus,i-1] + ctbi[bus,i-1] + sm * xbi[bus,i-1]
);

constraint forall(bus in b, i in 1..num_stops[bus]) (
    d_tbi[bus,i] >= tbi[bus,i] - tau_bi[bus,i] /\
    d_tbi[bus,i] >= tau_bi[bus,i] - tbi[bus,i] /\
    d_tbi[bus,i] <= mu /\
    ctbi[bus,i] >= psi * xbi[bus,i]
);

% -----------------------------
% C. INSTALACIÓN DE CARGADORES
% -----------------------------

constraint forall(bus in b, i in 1..num_stops[bus]) (
    beta * xbi[bus,i] >= ctbi[bus,i] /\
    xst[st_bi[bus,i]] >= xbi[bus,i]
);

% -----------------------------
% D. NO SOLAPAMIENTO DE CARGAS
% -----------------------------

constraint forall(bus1,bus2 in b where bus1 < bus2)(
    forall(i in 1..num_stops[bus1], j in 1..num_stops[bus2]
    where st_bi[bus1,i] == st_bi[bus2,j])(

        zbdij[bus1,bus2,i,j] <= xbi[bus1,i] /\
        zbdij[bus1,bus2,i,j] <= xbi[bus2,j] /\
        xbi[bus1,i] + xbi[bus2,j] <= zbdij[bus1,bus2,i,j] + 1 /\

        tbi[bus1,i] >= tbi[bus2,j] + ctbi[bus2,j] + sm - m * zbdi[bus1,bus2,i,j] /\
        tbi[bus2,j] >= tbi[bus1,i] + ctbi[bus1,i] + sm - m * zbdi[bus2,bus1,j,i] /\

        zbdi[bus1,bus2,i,j] + zbdi[bus2,bus1,j,i] - (1 - zbdij[bus1,bus2,i,j]) <= 1
    )
);

% -----------------------------
% E. ENERGÍA MÍNIMA REQUERIDA
% -----------------------------

constraint forall(bus in b)(
    sum(i in 1..num_stops[bus])(ebi[bus,i]) >=
    sum(i in 1..num_stops[bus])(d[bus,i]) - consumo_max + consumo_min
);

% -----------------------------
% F. FUNCIÓN OBJETIVO
% -----------------------------

solve minimize sum(s in st)(xst[s]);

% -----------------------------
% SALIDA DE RESULTADOS
% -----------------------------

output [
"estaciones instaladas: ", show(xst), "\n",
"total estaciones: ", show(sum(s in st)(xst[s])), "\n",
"desviacion total: ",
show(sum(bus in b, i in 1..max_stops)(d_tbi[bus,i])),
"\n"
];
