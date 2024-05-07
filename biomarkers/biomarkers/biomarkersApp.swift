//
//  biomarkersApp.swift
//  biomarkers
//
//  Created by Rishit Vora on 29/11/23.
//

import SwiftUI
import HealthKit
import Foundation

typealias StatisticMethod = (HKStatistics) -> Double?

struct QueryDetail {
	let option: HKStatisticsOptions
	let method: StatisticMethod
}


@main
struct BiomarkersApp: App {
	var body: some Scene {
		WindowGroup {
			ContentView()
				.onAppear {
					HealthKitManager.shared.requestAuthorization()
				}
		}
	}
}

class HealthKitManager {
	static let shared = HealthKitManager()
	private var healthStore: HKHealthStore?
	
	init() {
		if HKHealthStore.isHealthDataAvailable() {
			healthStore = HKHealthStore()
		}
	}
	
	func requestAuthorization() {
		let heathDataTypes = Set([
			HKObjectType.workoutType(),
			HKQuantityType.quantityType(forIdentifier: .heartRate)!,
			HKQuantityType.quantityType(forIdentifier: .vo2Max)!,
			HKQuantityType.quantityType(forIdentifier: .heartRateVariabilitySDNN)!,
			HKQuantityType.quantityType(forIdentifier: .restingHeartRate)!,
			HKObjectType.quantityType(forIdentifier: .activeEnergyBurned)!,
			HKObjectType.quantityType(forIdentifier: .distanceWalkingRunning)!,
			HKObjectType.quantityType(forIdentifier: .stepCount)!
		])
		DispatchQueue.main.async {
			self.healthStore?.requestAuthorization(toShare: nil, read: heathDataTypes) { success, error in
				if !success {
					print("Authorization failed: \(error?.localizedDescription ?? "Undefined error")")
				}
				else {
					self.executeQueriesForAllDataTypes()
				}
			}
		}
	}
	
	private func executeQueriesForAllDataTypes() {
		let queryDetails: [HKQuantityTypeIdentifier: QueryDetail] = [
			.heartRate: QueryDetail(
				option: .discreteAverage,
				method: { stats in
					stats.averageQuantity()?.doubleValue(for: HKUnit(from: "count/min"))
				}
			),
			.vo2Max: QueryDetail(
				option: .discreteAverage,
				method: { stats in
					stats.averageQuantity()?.doubleValue(for: HKUnit(from: "ml/kg/min"))
				}
			),
			.heartRateVariabilitySDNN: QueryDetail(
				option: .discreteAverage,
				method: { stats in
					stats.averageQuantity()?.doubleValue(for: HKUnit(from: "ms"))
				}
			),
			.restingHeartRate: QueryDetail(
				option: .discreteAverage,
				method: { stats in
					stats.averageQuantity()?.doubleValue(for: HKUnit(from: "count/min"))
				}
			),
			.activeEnergyBurned: QueryDetail(
				option: .cumulativeSum,
				method: { stats in
					stats.sumQuantity()?.doubleValue(for: HKUnit.kilocalorie())
				}
			),
			.distanceWalkingRunning: QueryDetail(
				option: .cumulativeSum,
				method: { stats in
					stats.sumQuantity()?.doubleValue(for: HKUnit.meter())
				}
			),
			.stepCount: QueryDetail(
				option: .cumulativeSum,
				method: { stats in
					stats.sumQuantity()?.doubleValue(for: HKUnit.count())
				}
			)
		]
		
		for (identifier, queryDetail) in queryDetails {
			executeHealthDataQuery(for: identifier, with: queryDetail)
		}
	}
	
	private func executeHealthDataQuery(for identifier: HKQuantityTypeIdentifier, with queryDetail: QueryDetail) {
		guard let quantityType = HKObjectType.quantityType(forIdentifier: identifier) else {
			return
		}
		let predicate = createCurrentWeekPredicate()
		let query = HKStatisticsCollectionQuery(
			quantityType: quantityType,
			quantitySamplePredicate: predicate,
			options: queryDetail.option,
			anchorDate: getStartOfWeek(),
			intervalComponents: DateComponents(day: 1)
		)
		
		query.initialResultsHandler = { query, results, error in
			if let statsCollection = results {
				self.processStatisticsCollection(for: statsCollection, with: queryDetail)
			}
			else {
				print("Error executing query for \(identifier.rawValue): \(error!.localizedDescription)")
			}
		}
		
		healthStore?.execute(query)
	}
	
	private func processStatisticsCollection(for statsCollection: HKStatisticsCollection, with queryDetail: QueryDetail) {
		var values: [Double] = []
		
		statsCollection.enumerateStatistics(from: getStartOfWeek(), to: Date()) { statistics, _ in
			let value = queryDetail.method(statistics) ?? 0.0
			values.append(value)
		}
	}
	
	private func getStartOfWeek() -> Date {
		let now = Date()
		let calendar = Calendar(identifier: .gregorian)
		let timezone = TimeZone(identifier: "Asia/Kolkata") ?? TimeZone.current
		var components = calendar.dateComponents(in: timezone, from: now)
		components.weekday = 2 // Monday
		components.hour = 0
		components.minute = 0
		components.second = 0

		// Calculate the start of this week, adjusting for the calendar's weekday start
		guard let startOfWeek = calendar.nextDate(after: now, matching: components, matchingPolicy: .nextTime, repeatedTimePolicy: .first, direction: .backward) else {
			fatalError("Failed to calculate the start of the week.")
		}
		
		return startOfWeek
	}
	
	private func createCurrentWeekPredicate() -> NSPredicate {
		let now = Date()
		let startOfWeek = getStartOfWeek()
		return HKQuery.predicateForSamples(withStart: startOfWeek, end: now, options: .strictStartDate)
	}
}


struct biomarkersAppView: View {
	var body: some View {
		Text("Hello World!")
	}
}

//print(HKHealthStore.isHealthDataAvailable())
