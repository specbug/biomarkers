//
//  biomarkersApp.swift
//  biomarkers
//
//  Created by Rishit Vora on 29/11/23.
//

import SwiftUI
import HealthKit


@main
struct biomarkersApp: App {
	var body: some Scene {
		WindowGroup {
			ContentView()
				.onAppear {
					requestHealthKitAuth()
				}
		}
	}
	
	func getLastWeekStartDate(from date: Date = Date()) -> Date {
		return Calendar.current.date(byAdding: .day, value: -6, to: date)!
	}

	func createLastWeekPredicate(from endDate: Date = Date()) -> NSPredicate {
		let startDate = getLastWeekStartDate(from: endDate)
		return HKQuery.predicateForSamples(withStart: startDate, end: endDate)
	}
	
	func createAnchorDate() -> Date {
		// Set the arbitrary anchor date to Monday at 3:00 a.m.
		let calendar: Calendar = .current
		var anchorComponents = calendar.dateComponents([.day, .month, .year, .weekday], from: Date())
		let offset = (7 + (anchorComponents.weekday ?? 0) - 2) % 7
		
		anchorComponents.day! -= offset
		anchorComponents.hour = 3
		
		let anchorDate = calendar.date(from: anchorComponents)!
		
		return anchorDate
	}
	
	
	
	private func requestHealthKitAuth() {
		var healthStore: HKHealthStore?
		if HKHealthStore.isHealthDataAvailable() {
			healthStore = HKHealthStore()
		}
		let allTypes = Set([HKObjectType.workoutType(),
							HKQuantityType.quantityType(forIdentifier: .stepCount)!,
							HKObjectType.quantityType(forIdentifier: .activeEnergyBurned)!,
							HKObjectType.quantityType(forIdentifier: .distanceCycling)!,
							HKObjectType.quantityType(forIdentifier: .distanceWalkingRunning)!,
							HKObjectType.quantityType(forIdentifier: .heartRate)!])
		DispatchQueue.main.async {
			healthStore?.requestAuthorization(toShare: nil, read: allTypes) { (success, error) in
				if !success {
					let errorMessage = error
					print(errorMessage ?? "Undefined error")
				}
				else {
					print("hehe")
					let initialResultsHandler: (HKStatisticsCollection) -> Void = { (statisticsCollection) in
						var values: [Double] = []
						statisticsCollection.enumerateStatistics(from: getLastWeekStartDate(), to: Date()) { (statistics, stop) in
							let statisticsQuantity = statistics.averageQuantity()
							let value = statisticsQuantity?.doubleValue(for: .meter())
							values.append(value!)
						}
						print("hi")
						print(values)
					}
					print("2")
					let query = HKStatisticsCollectionQuery(quantityType: HKObjectType.quantityType(forIdentifier: .heartRate)!,
															quantitySamplePredicate: createLastWeekPredicate(),
															options: .discreteAverage,
															anchorDate: createAnchorDate(),
															intervalComponents: DateComponents(day: 1))
							
					// Set the results handler
					query.initialResultsHandler = { query, results, error in
						if let statsCollection = results {
							print("hahaha")
							print(statsCollection)
							initialResultsHandler(statsCollection)
						}
						else {
							print("oh no!")
							print(error!)
						}
					}
					print(query)
					 
					healthStore?.execute(query)
				}
			}
		}
		
	}
}

struct biomarkersAppView: View {
	var body: some View {
		Text("Hello World!")
	}
}

//print(HKHealthStore.isHealthDataAvailable())
