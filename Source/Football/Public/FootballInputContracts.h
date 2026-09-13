#pragma once

#include "CoreMinimal.h"
#include "FootballInputContracts.generated.h"

UENUM(BlueprintType)
enum class EFootballGameplayAction : uint8
{
    None,
    Pass,
    Shoot,
    Dribble,
    Tackle,
    GoalkeeperSave
};

/*
 * Input is intent only. The server validates ownership, eligibility and
 * context before the fixed simulation can create an action or contact.
 */
USTRUCT(BlueprintType)
struct FOOTBALL_API FFootballInputIntent
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Input")
    FVector2D Move = FVector2D::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Input")
    FVector2D Facing = FVector2D(1.0f, 0.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Input")
    bool bSprint = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Input")
    bool bPass = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Input")
    bool bShoot = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Input")
    bool bTackle = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Input")
    bool bSkill = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Input")
    EFootballGameplayAction Action = EFootballGameplayAction::None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Input", meta=(ClampMin="0.0", ClampMax="1.0"))
    float ActionStrength = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Input")
    int32 TargetPlayerId = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Input")
    int32 ClientSequence = 0;
};

USTRUCT(BlueprintType)
struct FOOTBALL_API FFootballGameplayCommand
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Authority")
    int64 SimulationTick = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Authority")
    int32 OwnerPlayerId = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Input")
    FFootballInputIntent Intent;
};
