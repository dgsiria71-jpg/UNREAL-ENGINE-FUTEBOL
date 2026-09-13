# Pipeline de animação: Blender para Unreal

## Autoridade

Blender é a fonte canônica de geometria, skeleton intent, weights, morphs, materials e LOD source. Unreal recebe exports derivados e valida seus resultados. Nenhum import ou ajuste de Control Rig grava de volta no blend master.

Neymar v1.9 é uma fixture preservada. A produção do Neymar Master v2 está pausada. O pipeline precisa funcionar com um generic player e permitir substituir o Skeletal Mesh sem alterar a simulação ou CareerPlayer.

## Recovery para dados normalizados

O importador lê controller.ctrl, COFMotion, clips recuperados, root movement, ball marker, kickOutFrame, kickPoint e contact windows. Para cada ação, o normalizador produz:

    action_id
    source_motion_hashes
    source_state_hash
    skeleton_map
    frame_rate = 30
    root_translation / root_yaw
    bone_rotation_curves
    contact_marker
    kick_out_frame
    kick_point
    mirror_policy
    semantic_status
    provenance

XQuat40U, XNumber e valores raw ficam disponíveis para auditoria. Um nome lógico que não tem clip independente continua como ação lógica unresolved.

## Unreal assets

A sequência de admissão é:

    Blender canonical scene
      -> automated validation
      -> FBX or glTF export
      -> Unreal Skeletal Mesh / Skeleton
      -> Physics Asset
      -> Morph Targets
      -> IK Rig
      -> IK Retargeter
      -> Control Rig
      -> Animation Sequences and Pose Search Database
      -> Animation Blueprint

O exportador valida escala, orientação, bone names, bind pose, weights, morph topology, UVs, material slots, tangents, LODs e origem do arquivo. O importador não reconstrói Neymar; preserva o checkpoint e registra incompatibilidades.

## Pose Search e Motion Matching

Pose Search indexa poses e trajetória de clips normalizados. O query usa velocidade, aceleração, direção, orientação, fase, contacto, bola próxima e intenção atual. Motion Matching escolhe uma pose/apresentação entre candidatos e pode ser interrompido por uma ação com janela de contato.

Ele nunca decide:

- ball velocity;
- posse authoritative;
- gol;
- regra;
- resultado de tackle;
- propriedade de um CareerPlayer.

A cadeia é:

    input/AI intent
      -> gameplay action
      -> selected normalized clip/query
      -> kickOutFrame or kickPoint event
      -> BALL_CONTACT
      -> authoritative GetKickVelocity / ball simulation
      -> pose presentation

Se a simulação rejeitar o contato, a animação deve reconciliar para a pose/estado replicado. Não se cria “bola magnética” para esconder divergência.

## IK e Control Rig

IK Rig define retarget chains e goals de pés/mãos. IK Retargeter mapeia skeletons de jogadores genéricos e assets legados. Control Rig aplica correções de contato, equilíbrio, plant foot, look-at e relação corpo-bola na apresentação. Essas correções são limitadas e determinísticas no cliente visual; não mutam o resultado server-side.

## Qualidade

Validações de animação incluem foot sliding, popping, root drift, pose snapping, espelhamento, contato no frame correto, transições idle/walk/jog/run/sprint, aceleração/desaceleração, virada, primeiro toque, condução, passe, chute, cruzamento, drible, desarme, colisão, queda, recuperação e ações de goleiro. Testes em movimento usam broadcast e Player Career camera; screenshot isolado não encerra a validação.
