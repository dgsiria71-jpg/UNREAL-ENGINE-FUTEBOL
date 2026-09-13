#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "FootballGameMode.generated.h"

UCLASS()
class FOOTBALL_API AFootballGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    explicit AFootballGameMode(const FObjectInitializer& ObjectInitializer);
};
