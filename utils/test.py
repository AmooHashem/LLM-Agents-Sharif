import re
from typing import List


def parse_time(time_str: str) -> float:
    """
    Parses a time string "HH:MM:SS" or "HH:MM:SS.ss" into total seconds (float).
    """
    parts = time_str.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds


def format_time(sec: float) -> str:
    """
    Formats a float number of seconds into "HH:MM:SS" if whole seconds,
    or "HH:MM:SS.ss" with two decimal places if fractional.
    """
    hours = int(sec // 3600)
    minutes = int((sec % 3600) // 60)
    seconds_float = sec % 60
    if abs(seconds_float - round(seconds_float)) < 1e-6:
        seconds_int = int(round(seconds_float))
        return f"{hours:02d}:{minutes:02d}:{seconds_int:02d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{seconds_float:05.2f}"


def total_duration(segments: List[str]) -> str:
    """
    Given a list of segments in the format "HH:MM:SS – HH:MM:SS | Description",
    returns the sum of all segment durations as a formatted string "HH:MM:SS" or "HH:MM:SS.ss".
    """
    total_seconds = 0.0
    # Updated regex to also optionally capture description after pipe
    pattern = re.compile(
        r"^(?P<start>[\d:.]+)\s*–\s*(?P<end>[\d:.]+)(?:\s*\|\s*.+)?$"
    )

    for seg in segments:
        m = pattern.match(seg.strip())
        if not m:
            raise ValueError(f"Invalid segment format: {seg}")
        start_sec = parse_time(m.group("start"))
        end_sec = parse_time(m.group("end"))
        duration = end_sec - start_sec
        if duration < 0:
            raise ValueError(
                f"End time is before start time in segment: {seg}")
        total_seconds += duration

    return format_time(total_seconds)


# Example usage:
if __name__ == "__main__":
    segments = [
        "00:00:14 – 00:00:32 | Introduction to different types of models and the role of machine learning in tuning model parameters.",
        "00:00:35 – 00:00:50 | Overview of the lecture structure: linear predictors, loss minimization, and stochastic gradient descent.",
        "00:01:17 – 00:01:35 | Explanation of binary classification using spam classification as an example.",
        "00:01:53 – 00:02:10 | Introduction to different types of prediction problems: binary classification, regression, multi-class classification, ranking, and structured prediction.",
        "00:02:12 – 00:02:35 | Explanation of feature extraction and creation of feature vectors.",
        "00:02:53 – 00:03:10 | Importance of data in machine learning and the concept of training data.",
        "00:03:20 – 00:03:40 | Explanation of the learning algorithm and its output: the predictor.",
        "00:05:58 – 00:06:15 | Introduction to feature extraction and its role in linear prediction.",
        "00:06:42 – 00:07:05 | Example of feature extraction using an email address.",
        "00:08:08 – 00:08:30 | Explanation of feature vectors and their role in machine learning.",
        "00:10:17 – 00:10:35 | Introduction to weight vectors and their interpretation.",
        "00:11:00 – 00:11:20 | Explanation of the dot product between weight and feature vectors and its significance.",
        "00:15:10 – 00:15:30 | Summary of the relationship between weight vectors and feature vectors.",
        "00:16:05 – 00:16:25 | Definition of a linear classifier and its function.",
        "00:18:52 – 00:19:10 | Example of classification using a weight vector and feature vectors.",
        "00:15:10 – 00:16:46 | Introduction to feature vectors and weight vectors in linear classifiers / Explanation of linear classifiers and the role of the sign function",
        "00:17:19 – 00:18:22 | Geometric intuition of weight vectors and feature vectors",
        "00:18:52 – 00:19:02 | Classification example using weight and feature vectors",
        "00:19:08 – 00:19:30 | Explanation of decision boundaries in linear classifiers",
        "00:23:00 – 00:23:14 | Importance of weight vector direction in classification",
        "00:23:57 – 00:24:47 | Introduction to optimization and loss functions",
        "00:25:13 – 00:25:39 | Definition and purpose of loss functions in machine learning",
        "00:29:03 – 00:29:25 | Explanation of margin and its role in classification",
        "00:30:05 – 00:30:12 | Understanding when a binary classifier makes a mistake",
        "00:30:17 – 00:31:07 | Introduction to zero-one loss function",
        "00:33:32 – 00:34:09 | Overview of loss minimization framework",
        "00:30:15 – 00:31:12 | Explanation of zero-one loss function and its role in classification.",
        "00:31:42 – 00:32:22 | Visual representation of zero-one loss and its implications.",
        "00:33:32 – 00:34:36 | Introduction to linear regression and the concept of residuals.",
        "00:35:31 – 00:36:24 | Explanation of squared loss and its application in regression.",
        "00:37:28 – 00:38:38 | Discussion of different loss functions: squared loss, absolute deviation loss, and Huber loss.",
        "00:39:04 – 00:40:06 | Importance of minimizing average loss and trade-offs in machine learning.",
        "00:45:39 – 00:47:13 | Introduction to gradient descent and its application in optimization.",
        "00:48:04 – 00:49:38 | Detailed explanation of gradient computation for least squares regression.",
        "00:45:39 – 00:47:13 | Explanation of gradient descent and its mechanics.",
        "00:47:49 – 00:49:35 | Application of gradient descent to least squares regression.",
        "00:49:49 – 00:50:20 | Discussion on the role of the gradient in optimization.",
        "00:50:26 – 00:51:19 | Introduction to vector-based implementation using NumPy.",
        "00:55:11 – 00:55:35 | Explanation of generating artificial data for testing algorithms.",
        "00:59:48 – 01:00:31 | Introduction to stochastic gradient descent and its benefits.",
        "01:02:00 – 01:03:55 | Discussion on step size in stochastic gradient descent and its effects.",
        "01:04:00 – 01:05:03 | Implementation of stochastic gradient descent.",
        "01:00:31 – 01:01:09 | Introduction to stochastic gradient descent (SGD) and its key insight",
        "01:01:26 – 01:02:19 | Explanation of SGD algorithm and step size importance",
        "01:02:54 – 01:03:24 | Visual explanation of step size effects in SGD",
        "01:03:29 – 01:04:00 | Implementation of stochastic gradient descent",
        "01:04:55 – 01:05:50 | Detailed explanation of SGD implementation and step size schedule",
        "01:06:35 – 01:07:00 | Clarification on the stochastic nature of SGD",
        "01:07:11 – 01:07:57 | Demonstration of SGD's speed and efficiency compared to gradient descent",
        "01:12:12 – 01:12:28 | Summary of linear predictors and loss minimization",
        "01:12:48 – 01:13:47 | Introduction to zero-one loss and its limitations for gradient descent",
        "01:14:06 – 01:15:01 | Introduction to hinge loss as an alternative to zero-one loss",
        "01:15:08 – 01:16:01 | Explanation of hinge loss and its properties",
        "01:16:09 – 01:17:06 | Calculation of the gradient for hinge loss",
        "01:18:46 – 01:19:08 | Overview of logistic regression and loss minimization framework",
        "01:19:11 – 01:20:03 | Summary of classification and regression loss functions",
        "01:15:08 – 01:17:06 | Introduction to hinge loss and its role as a differentiable alternative to zero-one loss. / Explanation of how to compute the gradient of hinge loss and its significance in optimization. / Discussion on the conditions for the gradient of hinge loss and its application in stochastic gradient descent.",
        "01:17:15 – 01:17:45 | Explanation of the significance of the margin in classification and its role in support vector machines.",
        "01:18:46 – 01:19:08 | Overview of the general framework of loss minimization and its application to various prediction problems.",
        "01:19:11 – 01:19:55 | Summary of classification and regression techniques, including the use of different loss functions.",
        "01:20:00 – 01:20:09 | Discussion on optimization techniques like stochastic gradient descent and their advantages over gradient descent."
    ]
    print("Total duration:", total_duration(segments))
    # Expected: Total duration: 00:01:21  (which is (36 + 16 + 39) = 91 seconds = 00:01:31)
