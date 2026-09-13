#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GameplayTagContainer.h"
#include "FootballDataAssets.generated.h"

class USkeletalMesh;

UCLASS(BlueprintType)
class FOOTBALL_API UFootballPlayerDataAsset : public UPrimaryDataAsset
{
    GENERATED_BODY()

public:
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Identity")
    FName StableId;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Identity")
    FString ProvenanceHash;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Tuning")
    bool bProvisionalTuning = true;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Tuning")
    float MaxSpeedCmPerSecond = 0.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Visual")
    TSoftObjectPtr<USkeletalMesh> SkeletalMesh;
};

UCLASS(BlueprintType)
class FOOTBALL_API UFootballActionDataAsset : public UPrimaryDataAsset
{
    GENERATED_BODY()

public:
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Identity")
    FName StableId;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Recovery")
    FString RecoverySourceVersion = TEXT("unknown");

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Recovery")
    int32 ActionId = 0;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Recovery")
    int32 KickOutFrame = 0;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Recovery")
    bool bContactWindowResolved = false;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Recovery")
    bool bVelocitySemanticsResolved = false;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Gameplay")
    FGameplayTag ActionTag;
};

UCLASS(BlueprintType)
class FOOTBALL_API UFootballCompetitionDataAsset : public UPrimaryDataAsset
{
    GENERATED_BODY()

public:
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Competition")
    FName StableId;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Competition")
    int32 TeamCount = 0;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Competition")
    bool bHasGroupStage = false;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Competition")
    bool bHasKnockout = false;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Competition")
    bool bPromotionAndRelegation = false;
};
