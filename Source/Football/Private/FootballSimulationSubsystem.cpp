#include "FootballSimulationSubsystem.h"
#include "Football.h"

void UFootballSimulationSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    FixedStepSeconds = FMath::Clamp(FixedStepSeconds, 1.0f / 1000.0f, 0.25f);
    AccumulatorSeconds = 0.0f;
    SimulationTick = 0;
    BallState = FFootballBallState{};
    PendingCommands.Reset();
    PendingContacts.Reset();
}

void UFootballSimulationSubsystem::Deinitialize()
{
    PendingCommands.Reset();
    PendingContacts.Reset();
    Super::Deinitialize();
}

void UFootballSimulationSubsystem::Tick(float DeltaTime)
{
    AccumulatorSeconds += FMath::Max(0.0f, DeltaTime);

    int32 Steps = 0;
    constexpr int32 MaxStepsPerFrame = 8;
    while (AccumulatorSeconds >= FixedStepSeconds && Steps < MaxStepsPerFrame)
    {
        StepSimulation();
        AccumulatorSeconds -= FixedStepSeconds;
        ++Steps;
    }

    if (Steps == MaxStepsPerFrame && AccumulatorSeconds >= FixedStepSeconds)
    {
        UE_LOG(LogFootball, Warning,
            TEXT("Simulation catch-up capped; inspect frame budget before changing gameplay semantics."));
        AccumulatorSeconds = FMath::Fmod(AccumulatorSeconds, FixedStepSeconds);
    }
}

TStatId UFootballSimulationSubsystem::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UFootballSimulationSubsystem, STATGROUP_Tickables);
}

bool UFootballSimulationSubsystem::SubmitGameplayCommand(const FFootballGameplayCommand& Command)
{
    if (Command.OwnerPlayerId <= 0)
    {
        UE_LOG(LogFootball, Verbose,
            TEXT("Rejected gameplay command without an owner; ownership must be assigned by the server."));
        return false;
    }

    PendingCommands.Add(Command);
    return true;
}

bool UFootballSimulationSubsystem::SubmitAuthoritativeBallContact(const FFootballBallContact& Contact)
{
    if (!Contact.bAuthoritative || !Contact.bSemanticComplete || !Contact.bVelocityResolved)
    {
        UE_LOG(LogFootball, Verbose,
            TEXT("Rejected unresolved ball contact action=%d frame=%d; recovery gate is still open."),
            Contact.ActionId, Contact.ContactFrame);
        return false;
    }

    PendingContacts.Add(Contact);
    return true;
}

void UFootballSimulationSubsystem::StepSimulation()
{
    /*
     * Gameplay commands are consumed at a fixed tick by the future action
     * resolver. They never write BallState directly. Contact records are
     * already server-authorized and velocity-resolved.
     */
    PendingCommands.Reset();

    for (const FFootballBallContact& Contact : PendingContacts)
    {
        BallState.Position = Contact.KickPoint;
        BallState.Velocity = Contact.RecoveredVelocity;
        BallState.Kind = Contact.ResultingState;
    }
    PendingContacts.Reset();

    ++SimulationTick;
    BallState.SimulationTick = SimulationTick;
}
