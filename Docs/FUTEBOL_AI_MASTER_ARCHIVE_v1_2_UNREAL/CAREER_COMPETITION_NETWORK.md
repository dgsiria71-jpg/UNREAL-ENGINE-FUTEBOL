# Career Universe, Competition e rede

## Career Universe

Career state é um aggregate engine-independent com Players, CareerPlayers, Clubs, Seasons, Calendar, Contracts, Registrations, Transfers, Competitions, Fixtures, Standings, Brackets, Training, Development, Form, Morale, Fatigue, Injuries, Suspensions, ManagerTrust, History e background event stream.

PlayerDefinition descreve identidade/base; PlayerCardDefinition e CardInstance pertencem ao ecossistema de cartas; CareerPlayer pertence ao desenvolvimento e carreira. Roster, Squad, Formation e Tactics são referências de composição. Card progression não substitui Career development.

Own Player Only e Player Career Team Control são modos distintos. Manager Career fica separado. Uma partida de carreira constrói Match Setup do Career Universe, executa o mesmo Football Simulation, grava eventos/resultado e atualiza o aggregate.

## Competition Engine

League, Group Stage, Knockout, Playoff, Final, Cup, Qualification, Promotion e Relegation são fases parametrizadas. Fixtures, standings, brackets e sorteios determinísticos são dados/serviços, não classes duplicadas para cada formato. 5v5 e 11v11 usam a mesma engine com roster size, ruleset, duration e qualification config.

Os testes cobrem liga 8 clubes em turno/return, 14 rodadas/56 partidas, chave de knockout, grupos 4x4 com 6 jogos por grupo, promoção/rebaixamento e temporadas longas. Esses números são critérios de teste quando executados, não resultados presumidos.

## Co-op

Cada humano tem stable owner e CareerPlayer próprio. Transferências e contratos são eventos legítimos do universo; não existe teleporte de ownership. Votos de mudança exigem unanimidade conforme contrato do modo. Desconexão causa AI takeover temporário e reclaim pelo mesmo owner; outro cliente nunca assume seu CareerPlayer.

## Networking

Fluxo:

    local Enhanced Input
      -> input intent
      -> gameplay command
      -> Unreal Dedicated Server
           ownership validation
           fixed simulation
           Ball/Player/Rules/Match authority
      -> replication snapshot/event
      -> prediction/reconciliation
      -> local presentation

O servidor valida sequência, tick, owner e limites. O cliente prevê apenas o que o contrato permitir e reconcilia contra snapshots. Replication Graph/Iris são opções posteriores; primeiro medir relevância, número de actors, bandwidth, CPU e memória. Snapshot/command rates são configurados por perfil e não escolhidos para mascarar instabilidade.

Testes de rede incluem latência 0/30/80/150 ms, perda 1/2/3%, duplicação/reordenação, reconnect, dois ou mais owners e servidor headless. Gol, falta, tackle, posse e BALL_CONTACT são decididos somente no servidor.
