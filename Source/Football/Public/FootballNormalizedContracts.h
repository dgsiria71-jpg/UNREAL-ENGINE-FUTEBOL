#pragma once

#include "CoreMinimal.h"
#include "FootballNormalizedContracts.generated.h"

UENUM(BlueprintType)
enum class EFootballBallState : uint8
{
    Free,
    Controlled,
    Kicked,
    Deflected,
    GoalkeeperControlled,
    DeadRestart
};

UENUM(BlueprintType)
enum class EFootballContactProvenance : uint8
{
    NewGameAuthored,
    MobileRecovered
};

/*
 * Engine-facing normalized contact. The structure deliberately contains no
 * ball_impulse fallback. A contact is admissible only when the offline
 * recovery has resolved its velocity semantics.
 */
USTRUCT(BlueprintType)
struct FOOTBALL_API FFootballBallContact
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Recovery")
    int32 ActionId = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Recovery")
    int32 PlayerId = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Recovery")
    int32 ContactFrame = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Recovery")
    FVector KickPoint = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Recovery")
    FVector RecoveredVelocity = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Recovery")
    FString SourceVersion = TEXT("unknown");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Recovery")
    EFootballContactProvenance Provenance = EFootballContactProvenance::MobileRecovered;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Authority")
    bool bAuthoritative = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Authority")
    bool bSemanticComplete = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Authority")
    bool bVelocityResolved = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Recovery")
    EFootballBallState ResultingState = EFootballBallState::Kicked;
};

USTRUCT(BlueprintType)
struct FOOTBALL_API FFootballBallState
{
    GENERATED_BODY()

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Simulation")
    FVector Position = FVector::ZeroVector;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Simulation")
    FVector Velocity = FVector::ZeroVector;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Simulation")
    EFootballBallState Kind = EFootballBallState::Free;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Simulation")
    int64 SimulationTick = 0;
};
